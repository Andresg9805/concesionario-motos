import hashlib

import pytest

from app.domain.excepciones import (
    EventoIgnoradoError,
    FirmaInvalidaError,
    PagoInvalidoError,
    PasarelaNoDisponibleError,
)
from app.domain.pagos_envios import EstadoPago, MetodoPago, Pago
from app.infrastructure.externos.wompi import PasarelaWompi, calcular_firma_integridad
from tests.domain import fabricas
from tests.pedidos.conftest import CONFIGURACION_WOMPI, evento_firmado, transaccion

REFERENCIA = "CM-PED-12-1731700000"
MONTO_COP = 2 * 250_000 + 12_000


def pago_de_prueba():
    return Pago.para_pedido(fabricas.pedido(), REFERENCIA, MetodoPago.TARJETA)


def pasarela_con(respuestas):
    return PasarelaWompi(CONFIGURACION_WOMPI, lambda url: respuestas(url))


def test_la_firma_de_integridad_es_sha256_de_referencia_monto_moneda_y_secreto():
    esperada = hashlib.sha256(f"{REFERENCIA}51200000COPsecreto".encode()).hexdigest()
    assert calcular_firma_integridad(REFERENCIA, 51_200_000, "secreto") == esperada


def test_datos_para_widget_incluye_llave_referencia_monto_en_centavos_y_firma():
    datos = pasarela_con(lambda url: {}).datos_para_widget(pago_de_prueba())
    assert datos == {
        "llave_publica": CONFIGURACION_WOMPI.llave_publica,
        "referencia": REFERENCIA,
        "monto_centavos": MONTO_COP * 100,
        "moneda": "COP",
        "firma_integridad": calcular_firma_integridad(
            REFERENCIA, MONTO_COP * 100, CONFIGURACION_WOMPI.secreto_integridad
        ),
    }


@pytest.mark.parametrize(
    ("estado_wompi", "estado_interno"),
    [
        ("APPROVED", EstadoPago.APROBADO),
        ("DECLINED", EstadoPago.RECHAZADO),
        ("VOIDED", EstadoPago.RECHAZADO),
        ("ERROR", EstadoPago.ERROR),
        ("PENDING", EstadoPago.PENDIENTE),
    ],
)
def test_consultar_transaccion_mapea_los_estados_de_wompi(estado_wompi, estado_interno):
    urls = []

    def responder(url):
        urls.append(url)
        return {"data": transaccion("t-9", REFERENCIA, estado_wompi, MONTO_COP)}

    resultado = pasarela_con(responder).consultar_transaccion("t-9")
    assert urls == ["https://sandbox.wompi.test/v1/transactions/t-9"]
    assert resultado.estado == estado_interno
    assert resultado.referencia == REFERENCIA
    assert resultado.transaccion_id == "t-9"
    assert resultado.monto_cop == MONTO_COP


def test_consultar_transaccion_codifica_el_identificador_en_la_url():
    urls = []

    def responder(url):
        urls.append(url)
        return {"data": transaccion("a/b", REFERENCIA, "APPROVED", MONTO_COP)}

    pasarela_con(responder).consultar_transaccion("a/b?x=1")
    assert urls == ["https://sandbox.wompi.test/v1/transactions/a%2Fb%3Fx%3D1"]


@pytest.mark.parametrize(
    "datos",
    [
        None,
        {},
        {"id": "t", "status": "APPROVED", "reference": "r"},
        {"id": "t", "status": "NUEVO", "reference": "r", "amount_in_cents": 100},
        {"id": "t", "status": "APPROVED", "reference": "r", "amount_in_cents": 150},
        {
            "id": "t",
            "status": "APPROVED",
            "reference": "r",
            "amount_in_cents": 100,
            "currency": "USD",
        },
    ],
)
def test_una_respuesta_de_wompi_incompleta_o_invalida_se_rechaza(datos):
    with pytest.raises(PagoInvalidoError):
        pasarela_con(lambda url: {"data": datos}).consultar_transaccion("t")


def test_los_fallos_de_transporte_se_propagan_como_pasarela_no_disponible():
    def caer(url):
        raise PasarelaNoDisponibleError("sin red")

    with pytest.raises(PasarelaNoDisponibleError):
        pasarela_con(caer).consultar_transaccion("t")


def test_leer_evento_valido_devuelve_el_resultado_del_pago():
    evento = evento_firmado(transaccion("t-1", REFERENCIA, "APPROVED", MONTO_COP))
    resultado = pasarela_con(lambda url: {}).leer_evento(evento)
    assert resultado.estado == EstadoPago.APROBADO
    assert resultado.referencia == REFERENCIA
    assert resultado.monto_cop == MONTO_COP


def test_el_checksum_sigue_la_especificacion_de_eventos_de_wompi():
    evento = evento_firmado(transaccion("t-1", REFERENCIA, "APPROVED", MONTO_COP))
    cadena = f"t-1APPROVED{MONTO_COP * 100}1731700000{CONFIGURACION_WOMPI.secreto_eventos}"
    assert evento["signature"]["checksum"] == hashlib.sha256(cadena.encode()).hexdigest()


def test_leer_evento_acepta_el_checksum_en_mayusculas():
    evento = evento_firmado(transaccion("t-1", REFERENCIA, "APPROVED", MONTO_COP))
    evento["signature"]["checksum"] = evento["signature"]["checksum"].upper()
    assert pasarela_con(lambda url: {}).leer_evento(evento).estado == EstadoPago.APROBADO


def test_leer_evento_con_secreto_distinto_se_rechaza():
    evento = evento_firmado(transaccion("t-1", REFERENCIA, "APPROVED", MONTO_COP), secreto="x")
    with pytest.raises(FirmaInvalidaError):
        pasarela_con(lambda url: {}).leer_evento(evento)


def test_leer_evento_con_propiedad_firmada_ausente_se_rechaza():
    evento = evento_firmado(transaccion("t-1", REFERENCIA, "APPROVED", MONTO_COP))
    evento["signature"]["properties"].append("transaction.no_existe")
    with pytest.raises(FirmaInvalidaError):
        pasarela_con(lambda url: {}).leer_evento(evento)


def test_leer_evento_de_otro_tipo_con_firma_valida_se_ignora():
    evento = evento_firmado(transaccion("t-1", REFERENCIA, "APPROVED", MONTO_COP))
    evento["event"] = "nequi_token.updated"
    with pytest.raises(EventoIgnoradoError):
        pasarela_con(lambda url: {}).leer_evento(evento)
