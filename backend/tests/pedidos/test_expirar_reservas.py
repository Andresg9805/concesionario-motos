from datetime import timedelta

import pytest

from app.application.pedidos import ExpirarReservas
from app.domain.tienda import EstadoPedido, ItemPedido, Pedido
from app.infrastructure.memoria.pedidos import RepositorioPedidosEnMemoria
from app.infrastructure.memoria.tienda import RepositorioAccesoriosEnMemoria
from tests.domain import fabricas

AHORA = fabricas.AHORA


@pytest.fixture
def accesorios():
    return RepositorioAccesoriosEnMemoria([fabricas.accesorio(stock=5)])


@pytest.fixture
def pedidos(accesorios):
    return RepositorioPedidosEnMemoria(accesorios)


@pytest.fixture
def pedido(accesorios, pedidos):
    usuario = fabricas.cliente_usuario()
    casco = accesorios.listar()[0]
    nuevo = Pedido.crear(
        usuario,
        fabricas.direccion(usuario),
        [ItemPedido.desde_accesorio(casco, 2)],
        AHORA,
    )
    return pedidos.crear_con_reserva(nuevo)


def stock(accesorios):
    return accesorios.listar()[0].stock


def expirar_a_las(pedidos, accesorios, minutos):
    ExpirarReservas(pedidos, accesorios, lambda: AHORA + timedelta(minutes=minutos)).ejecutar()


def test_crear_el_pedido_reserva_el_stock(accesorios, pedido):
    assert pedido.estado == EstadoPedido.PENDIENTE_PAGO
    assert stock(accesorios) == 3


def test_un_pedido_vencido_pasa_a_expirado_y_devuelve_el_stock(accesorios, pedidos, pedido):
    expirar_a_las(pedidos, accesorios, minutos=16)

    assert pedidos.buscar_por_id(pedido.id).estado == EstadoPedido.EXPIRADO
    assert stock(accesorios) == 5


def test_un_pedido_que_no_ha_vencido_no_se_toca(accesorios, pedidos, pedido):
    expirar_a_las(pedidos, accesorios, minutos=10)

    assert pedidos.buscar_por_id(pedido.id).estado == EstadoPedido.PENDIENTE_PAGO
    assert stock(accesorios) == 3


def test_un_pedido_pagado_no_se_expira(accesorios, pedidos, pedido):
    pedido.marcar_pagado()
    pedidos.guardar(pedido)

    expirar_a_las(pedidos, accesorios, minutos=60)

    assert pedidos.buscar_por_id(pedido.id).estado == EstadoPedido.PAGADO
    assert stock(accesorios) == 3


def test_correr_la_expiracion_dos_veces_no_devuelve_el_stock_dos_veces(accesorios, pedidos, pedido):
    expirar_a_las(pedidos, accesorios, minutos=16)
    expirar_a_las(pedidos, accesorios, minutos=30)

    assert stock(accesorios) == 5
