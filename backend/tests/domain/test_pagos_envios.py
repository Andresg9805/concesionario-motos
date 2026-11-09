from datetime import timedelta

import pytest

from app.domain.excepciones import (
    PagoInvalidoError,
    PedidoInvalidoError,
    TransicionInvalidaError,
)
from app.domain.pagos_envios import (
    Envio,
    EstadoEnvio,
    EstadoPago,
    MetodoPago,
    Pago,
    ResultadoPago,
)
from tests.domain import fabricas


def pago() -> Pago:
    return Pago.para_pedido(fabricas.pedido(), "CM-PED-1", MetodoPago.NEQUI)


def resultado(estado: EstadoPago, monto: int = 512_000, referencia: str = "CM-PED-1"):
    return ResultadoPago(
        referencia=referencia, transaccion_id="TX-1", estado=estado, monto_cop=monto
    )


def test_pago_toma_el_total_del_pedido():
    nuevo = pago()
    assert nuevo.monto_cop == 512_000
    assert nuevo.monto_en_centavos() == 51_200_000
    assert nuevo.estado == EstadoPago.PENDIENTE


def test_monto_distinto_al_del_pedido_no_es_valido():
    with pytest.raises(PagoInvalidoError):
        Pago(
            pedido=fabricas.pedido(),
            referencia="CM-PED-1",
            metodo=MetodoPago.PSE,
            monto_cop=1_000,
        )


def test_aprobar_guarda_la_transaccion():
    nuevo = pago()
    nuevo.aprobar("TX-9")
    assert nuevo.estado == EstadoPago.APROBADO
    assert nuevo.transaccion_id == "TX-9"


def test_pago_aprobado_no_se_rechaza():
    nuevo = pago()
    nuevo.aprobar("TX-9")
    with pytest.raises(TransicionInvalidaError):
        nuevo.rechazar()


def test_actualizar_con_resultado_aprobado():
    nuevo = pago()
    assert nuevo.actualizar_con(resultado(EstadoPago.APROBADO))
    assert nuevo.estado == EstadoPago.APROBADO


def test_mismo_resultado_dos_veces_no_cambia_nada():
    nuevo = pago()
    nuevo.actualizar_con(resultado(EstadoPago.APROBADO))
    assert not nuevo.actualizar_con(resultado(EstadoPago.APROBADO))
    assert nuevo.estado == EstadoPago.APROBADO


def test_resultado_rechazado():
    nuevo = pago()
    assert nuevo.actualizar_con(resultado(EstadoPago.RECHAZADO))
    assert nuevo.estado == EstadoPago.RECHAZADO


def test_resultado_con_error():
    nuevo = pago()
    assert nuevo.actualizar_con(resultado(EstadoPago.ERROR))
    assert nuevo.estado == EstadoPago.ERROR


def test_resultado_pendiente_no_cambia_nada():
    assert not pago().actualizar_con(resultado(EstadoPago.PENDIENTE))


def test_resultado_con_otro_monto_es_invalido():
    with pytest.raises(PagoInvalidoError):
        pago().actualizar_con(resultado(EstadoPago.APROBADO, monto=1_000))


def test_resultado_de_otra_referencia_es_invalido():
    with pytest.raises(PagoInvalidoError):
        pago().actualizar_con(resultado(EstadoPago.APROBADO, referencia="OTRA"))


def test_envio_solo_para_pedidos_pagados():
    with pytest.raises(PedidoInvalidoError):
        Envio.crear(fabricas.pedido(), "GUIA-1", fabricas.AHORA)


def pedido_pagado():
    pedido = fabricas.pedido()
    pedido.marcar_pagado()
    return pedido


def test_envio_empieza_preparando_con_su_evento():
    envio = Envio.crear(pedido_pagado(), "GUIA-1", fabricas.AHORA)
    assert envio.estado == EstadoEnvio.PREPARANDO
    assert envio.costo_cop == 12_000
    assert len(envio.eventos) == 1


def test_envio_avanza_paso_a_paso_y_guarda_la_linea_de_tiempo():
    envio = Envio.crear(pedido_pagado(), "GUIA-1", fabricas.AHORA)
    for horas, estado in enumerate(
        (EstadoEnvio.ENVIADO, EstadoEnvio.EN_CAMINO, EstadoEnvio.ENTREGADO), start=1
    ):
        envio.avanzar(estado, "", fabricas.AHORA + timedelta(hours=horas))
    assert envio.estado == EstadoEnvio.ENTREGADO
    assert [evento.estado for evento in envio.eventos] == list(EstadoEnvio)


def test_envio_no_se_salta_estados():
    envio = Envio.crear(pedido_pagado(), "GUIA-1", fabricas.AHORA)
    with pytest.raises(TransicionInvalidaError):
        envio.avanzar(EstadoEnvio.ENTREGADO, "", fabricas.AHORA)


def test_envio_entregado_no_avanza_mas():
    envio = Envio.crear(pedido_pagado(), "GUIA-1", fabricas.AHORA)
    for estado in (EstadoEnvio.ENVIADO, EstadoEnvio.EN_CAMINO, EstadoEnvio.ENTREGADO):
        envio.avanzar(estado, "", fabricas.AHORA)
    with pytest.raises(TransicionInvalidaError):
        envio.avanzar(EstadoEnvio.ENTREGADO, "", fabricas.AHORA)
