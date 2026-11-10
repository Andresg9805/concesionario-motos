from datetime import timedelta

import pytest

from app.domain.excepciones import (
    PedidoInvalidoError,
    StockInsuficienteError,
    TransicionInvalidaError,
)
from app.domain.tienda import EstadoPedido, ItemPedido, Pedido
from tests.domain import fabricas


def test_reservar_descuenta_stock():
    accesorio = fabricas.accesorio(stock=5)
    accesorio.reservar(2)
    assert accesorio.stock == 3


def test_no_se_reserva_mas_de_lo_que_hay():
    with pytest.raises(StockInsuficienteError):
        fabricas.accesorio(stock=1).reservar(2)


def test_liberar_devuelve_stock():
    accesorio = fabricas.accesorio(stock=0)
    accesorio.liberar(3)
    assert accesorio.stock == 3


def test_cantidad_cero_no_es_valida():
    with pytest.raises(PedidoInvalidoError):
        fabricas.accesorio().reservar(0)


def test_item_toma_el_precio_del_accesorio():
    item = ItemPedido.desde_accesorio(fabricas.accesorio(precio_cop=250_000), 2)
    assert item.precio_unitario_cop == 250_000
    assert item.subtotal() == 500_000


def test_pedido_calcula_el_total_en_el_backend():
    pedido = fabricas.pedido()
    assert pedido.subtotal_cop == 500_000
    assert pedido.costo_envio_cop == 12_000
    assert pedido.total_cop() == 512_000


def test_pedido_queda_reservado_15_minutos():
    pedido = fabricas.pedido()
    assert pedido.estado == EstadoPedido.PENDIENTE_PAGO
    assert pedido.reservado_hasta == fabricas.AHORA + timedelta(minutes=15)


def test_reserva_vencida_despues_de_15_minutos():
    pedido = fabricas.pedido()
    assert not pedido.reserva_vencida(fabricas.AHORA + timedelta(minutes=15))
    assert pedido.reserva_vencida(fabricas.AHORA + timedelta(minutes=16))


def test_pedido_pagado_ya_no_vence():
    pedido = fabricas.pedido()
    pedido.marcar_pagado()
    assert not pedido.reserva_vencida(fabricas.AHORA + timedelta(hours=1))


def test_pedido_sin_items_no_es_valido():
    usuario = fabricas.cliente_usuario()
    with pytest.raises(PedidoInvalidoError):
        Pedido.crear(usuario, fabricas.direccion(usuario), [], fabricas.AHORA)


def test_no_se_usa_la_direccion_de_otro_cliente():
    usuario = fabricas.cliente_usuario()
    otro = fabricas.cliente_usuario(correo="otro@correo.com")
    items = [ItemPedido.desde_accesorio(fabricas.accesorio(), 1)]
    with pytest.raises(PedidoInvalidoError):
        Pedido.crear(usuario, fabricas.direccion(otro), items, fabricas.AHORA)


def test_subtotal_que_no_cuadra_con_los_items_falla():
    usuario = fabricas.cliente_usuario()
    with pytest.raises(PedidoInvalidoError):
        Pedido(
            usuario=usuario,
            direccion=fabricas.direccion(usuario),
            items=[ItemPedido.desde_accesorio(fabricas.accesorio(), 1)],
            subtotal_cop=1,
            costo_envio_cop=12_000,
            creado_en=fabricas.AHORA,
            reservado_hasta=fabricas.AHORA + timedelta(minutes=15),
        )


def test_expirar_un_pedido_pendiente():
    pedido = fabricas.pedido()
    pedido.expirar()
    assert pedido.estado == EstadoPedido.EXPIRADO


def test_pedido_expirado_no_se_puede_pagar():
    pedido = fabricas.pedido()
    pedido.expirar()
    with pytest.raises(TransicionInvalidaError):
        pedido.marcar_pagado()


def test_pedido_pagado_no_expira():
    pedido = fabricas.pedido()
    pedido.marcar_pagado()
    with pytest.raises(TransicionInvalidaError):
        pedido.expirar()
