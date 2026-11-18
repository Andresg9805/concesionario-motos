import pytest

from app.domain.estados_cotizacion import (
    ESTADOS,
    ESTADOS_CERRADOS,
    Contactado,
    EstadoAtencion,
    EstadoDeCotizacion,
    Nuevo,
    Vendido,
    estado_de,
)
from app.domain.excepciones import TransicionInvalidaError
from tests.domain.fabricas import cotizacion


def test_hay_un_objeto_estado_por_cada_valor_del_enum():
    assert set(ESTADOS) == set(EstadoAtencion)
    assert all(isinstance(estado, EstadoDeCotizacion) for estado in ESTADOS.values())
    assert all(clave == estado.clave for clave, estado in ESTADOS.items())


def test_cada_estado_decide_a_cuales_puede_pasar():
    assert isinstance(estado_de(EstadoAtencion.NUEVO), Nuevo)
    assert Nuevo().siguientes() == {EstadoAtencion.CONTACTADO, EstadoAtencion.DESCARTADO}
    assert EstadoAtencion.TEST_DRIVE in Contactado().siguientes()
    assert Vendido().siguientes() == frozenset()


def test_pasar_a_un_estado_valido_devuelve_el_objeto_del_nuevo_estado():
    assert isinstance(Nuevo().pasar_a(EstadoAtencion.CONTACTADO), Contactado)


def test_un_salto_invalido_lanza_error():
    with pytest.raises(TransicionInvalidaError, match="NUEVO a VENDIDO"):
        Nuevo().pasar_a(EstadoAtencion.VENDIDO)


def test_vendido_y_descartado_son_los_estados_cerrados():
    assert ESTADOS_CERRADOS == {EstadoAtencion.VENDIDO, EstadoAtencion.DESCARTADO}
    assert not estado_de(EstadoAtencion.DESCARTADO).esta_abierta()
    assert estado_de(EstadoAtencion.NEGOCIANDO).esta_abierta()


def test_cada_estado_tiene_su_mensaje_para_el_cliente():
    mensajes = {estado.mensaje_para_cliente() for estado in ESTADOS.values()}
    assert len(mensajes) == len(ESTADOS)


def test_la_cotizacion_delega_en_su_estado_el_cambio_y_si_esta_abierta():
    atencion = cotizacion()
    assert isinstance(atencion.situacion, Nuevo)
    atencion.cambiar_estado(EstadoAtencion.CONTACTADO)
    atencion.cambiar_estado(EstadoAtencion.NEGOCIANDO)
    atencion.cambiar_estado(EstadoAtencion.VENDIDO)
    assert atencion.estado == EstadoAtencion.VENDIDO
    assert not atencion.esta_abierta()
    with pytest.raises(TransicionInvalidaError):
        atencion.cambiar_estado(EstadoAtencion.DESCARTADO)
