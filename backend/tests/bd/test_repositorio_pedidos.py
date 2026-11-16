from datetime import datetime, timedelta

import pytest

from app.application.atencion import ZONA_COLOMBIA
from app.application.pedidos import ExpirarReservas
from app.domain.excepciones import StockInsuficienteError
from app.domain.pagos_envios import Envio, EstadoEnvio, EstadoPago, MetodoPago, Pago
from app.domain.tienda import Direccion, EstadoPedido, ItemPedido, Pedido
from app.infrastructure.db.repositorios.conversiones import usuario_a_dominio
from app.infrastructure.db.repositorios.pedidos import (
    RepositorioEnviosSQLAlchemy,
    RepositorioPagosSQLAlchemy,
    RepositorioPedidosSQLAlchemy,
)
from app.infrastructure.db.repositorios.tienda import (
    RepositorioAccesoriosSQLAlchemy,
    RepositorioDireccionesSQLAlchemy,
    RepositorioUbicacionesSQLAlchemy,
)
from tests.bd.datos import crear_accesorio, crear_ubicacion, crear_usuario

AHORA = datetime(2026, 11, 16, 10, 0, tzinfo=ZONA_COLOMBIA)


@pytest.fixture
def datos(sesion):
    municipio = crear_ubicacion(sesion)
    cliente = crear_usuario(sesion, "Ana Pérez", "ana@correo.com", "3001234567", "CLIENTE")
    casco = crear_accesorio(sesion, stock=5, precio_cop=3_000_000)
    guantes = crear_accesorio(
        sesion,
        sku="ALP-GUA-001",
        nombre="Guantes",
        categoria="GUANTES",
        fabricante="Alpinestars",
        stock=1,
        precio_cop=350_000,
    )
    usuario = usuario_a_dominio(cliente)
    ubicacion = RepositorioUbicacionesSQLAlchemy(sesion).buscar_municipio(municipio.codigo)
    assert ubicacion is not None
    direccion = RepositorioDireccionesSQLAlchemy(sesion).guardar(
        Direccion(
            usuario=usuario,
            municipio=ubicacion,
            detalle="Calle 10 # 5-20",
            telefono_contacto="3001234567",
            nombre_recibe="Ana Pérez",
        )
    )
    accesorios = RepositorioAccesoriosSQLAlchemy(sesion)
    return {
        "usuario": usuario,
        "direccion": direccion,
        "casco": accesorios.buscar_por_id(casco.id),
        "guantes": accesorios.buscar_por_id(guantes.id),
        "accesorios": accesorios,
    }


@pytest.fixture
def pedidos(sesion):
    return RepositorioPedidosSQLAlchemy(sesion)


def nuevo_pedido(datos, *items, ahora=AHORA):
    return Pedido.crear(
        datos["usuario"],
        datos["direccion"],
        [ItemPedido.desde_accesorio(accesorio, cantidad) for accesorio, cantidad in items],
        ahora,
    )


def test_crear_pedido_descuenta_el_stock(datos, pedidos):
    creado = pedidos.crear_con_reserva(nuevo_pedido(datos, (datos["casco"], 2)))

    assert creado.id is not None
    assert creado.estado == EstadoPedido.PENDIENTE_PAGO
    assert creado.subtotal_cop == 6_000_000
    assert creado.total_cop() == 6_012_000
    casco = datos["accesorios"].buscar_por_id(datos["casco"].id)
    assert casco.stock == 3


def test_si_un_accesorio_no_alcanza_no_se_descuenta_nada(datos, pedidos):
    pedido = nuevo_pedido(datos, (datos["casco"], 2), (datos["guantes"], 3))

    with pytest.raises(StockInsuficienteError):
        pedidos.crear_con_reserva(pedido)

    assert datos["accesorios"].buscar_por_id(datos["casco"].id).stock == 5
    assert datos["accesorios"].buscar_por_id(datos["guantes"].id).stock == 1
    assert pedidos.listar_por_usuario(datos["usuario"].id) == []


def test_buscar_y_listar_pedidos_del_usuario(datos, pedidos):
    creado = pedidos.crear_con_reserva(nuevo_pedido(datos, (datos["casco"], 1)))

    encontrado = pedidos.buscar_por_id(creado.id)
    assert encontrado is not None
    assert encontrado.items[0].accesorio.nombre == "X-Fifteen"
    assert encontrado.creado_en == AHORA
    assert [p.id for p in pedidos.listar_por_usuario(datos["usuario"].id)] == [creado.id]
    assert [p.id for p in pedidos.listar()] == [creado.id]


def test_listar_vencidos_solo_trae_pendientes_con_reserva_vencida(datos, pedidos):
    vencido = pedidos.crear_con_reserva(
        nuevo_pedido(datos, (datos["casco"], 1), ahora=AHORA - timedelta(hours=1))
    )
    pedidos.crear_con_reserva(nuevo_pedido(datos, (datos["casco"], 1)))

    assert [p.id for p in pedidos.listar_vencidos(AHORA)] == [vencido.id]


def test_expirar_reservas_devuelve_el_stock(datos, pedidos):
    pedidos.crear_con_reserva(
        nuevo_pedido(datos, (datos["casco"], 2), ahora=AHORA - timedelta(hours=1))
    )

    ExpirarReservas(pedidos, datos["accesorios"], lambda: AHORA).ejecutar()

    assert datos["accesorios"].buscar_por_id(datos["casco"].id).stock == 5
    assert pedidos.listar_vencidos(AHORA) == []


def test_pago_y_eventos_sin_repetir(sesion, datos, pedidos):
    pedido = pedidos.crear_con_reserva(nuevo_pedido(datos, (datos["casco"], 1)))
    pagos = RepositorioPagosSQLAlchemy(sesion, reloj=lambda: AHORA)

    pago = pagos.guardar(Pago.para_pedido(pedido, "CM-REF-001", MetodoPago.TARJETA))
    assert pago.estado == EstadoPago.PENDIENTE
    assert pago.transaccion_id is None

    pago.aprobar("tx-123")
    pagos.guardar(pago)

    encontrado = pagos.buscar_por_referencia("CM-REF-001")
    assert encontrado is not None
    assert encontrado.estado == EstadoPago.APROBADO
    assert encontrado.transaccion_id == "tx-123"
    assert pagos.buscar_por_pedido(pedido.id).referencia == "CM-REF-001"

    assert pagos.registrar_evento(pago.id, "checksum-1") is True
    assert pagos.registrar_evento(pago.id, "checksum-1") is False
    assert pagos.registrar_evento(pago.id, "checksum-2") is True


def test_envio_guarda_solo_eventos_y_calcula_estado_y_costo(sesion, datos, pedidos):
    pedido = pedidos.crear_con_reserva(nuevo_pedido(datos, (datos["casco"], 1)))
    pedido.marcar_pagado()
    pedido = pedidos.guardar(pedido)
    envios = RepositorioEnviosSQLAlchemy(sesion)

    envio = envios.guardar(Envio.crear(pedido, "CM-GUIA-0001", AHORA))
    envio.avanzar(EstadoEnvio.ENVIADO, "Salió de bodega", AHORA + timedelta(hours=2))
    envios.guardar(envio)

    encontrado = envios.buscar_por_pedido(pedido.id)
    assert encontrado is not None
    assert encontrado.estado == EstadoEnvio.ENVIADO
    assert encontrado.costo_cop == 12_000
    assert [e.estado for e in encontrado.eventos] == [
        EstadoEnvio.PREPARANDO,
        EstadoEnvio.ENVIADO,
    ]
    assert [e.numero_guia for e in envios.listar()] == ["CM-GUIA-0001"]
    por_id = envios.buscar_por_id(encontrado.id)
    assert por_id is not None
    assert por_id.estado == EstadoEnvio.ENVIADO
    assert envios.buscar_por_id(99) is None
