import asyncio
from datetime import date

import httpx
import pytest

from app.domain.excepciones import TasaNoDisponibleError
from app.infrastructure.externos.circuit_breaker import CircuitBreaker, EstadoCircuito
from app.infrastructure.externos.trm import (
    URL_TRM,
    ProveedorTasaCambioDatosGov,
    url_trm_configurada,
)

RESPUESTA = [
    {
        "valor": "4125.50",
        "unidad": "COP",
        "vigenciadesde": "2026-11-16T00:00:00.000",
        "vigenciahasta": "2026-11-16T00:00:00.000",
    }
]


class Servidor:
    def __init__(self, *respuestas):
        self.respuestas = list(respuestas)
        self.peticiones = []

    def __call__(self, peticion):
        self.peticiones.append(peticion)
        respuesta = self.respuestas.pop(0)
        if isinstance(respuesta, Exception):
            raise respuesta
        return respuesta

    def proveedor(self, **kwargs):
        return ProveedorTasaCambioDatosGov(
            transporte=httpx.MockTransport(self),
            **kwargs,
        )


def ok(cuerpo=RESPUESTA):
    return httpx.Response(200, json=cuerpo)


def obtener(proveedor):
    return asyncio.run(proveedor.obtener_trm())


def test_parsea_la_trm_de_datos_gov():
    servidor = Servidor(ok())
    trm = obtener(servidor.proveedor())
    assert trm.valor == 4125.50
    assert trm.fecha == date(2026, 11, 16)


def test_consulta_la_url_de_la_trm_vigente_con_timeout_de_3_segundos():
    servidor = Servidor(ok())
    obtener(servidor.proveedor())
    peticion = servidor.peticiones[0]
    assert peticion.url.host == "www.datos.gov.co"
    assert peticion.url.path == "/resource/32sa-8pi3.json"
    assert peticion.url.params["$order"] == "vigenciadesde DESC"
    assert peticion.url.params["$limit"] == "1"
    assert peticion.extensions["timeout"] == {
        "connect": 3.0,
        "read": 3.0,
        "write": 3.0,
        "pool": 3.0,
    }


def test_permite_sobreescribir_la_url(monkeypatch):
    assert url_trm_configurada() == URL_TRM
    monkeypatch.setenv("TRM_API_URL", " https://ejemplo.test/trm.json ")
    assert url_trm_configurada() == "https://ejemplo.test/trm.json"


@pytest.mark.parametrize(
    "falla",
    [
        httpx.ReadTimeout("lento"),
        httpx.ConnectError("sin red"),
        httpx.Response(500),
        httpx.Response(404),
        ok([]),
        ok([{"valor": "no-es-un-numero", "vigenciadesde": "2026-11-16T00:00:00.000"}]),
        ok([{"valor": "0", "vigenciadesde": "2026-11-16T00:00:00.000"}]),
        ok([{"vigenciadesde": "2026-11-16T00:00:00.000"}]),
    ],
)
def test_los_errores_cuentan_como_fallo_del_circuito(falla):
    servidor = Servidor(ok(), falla)
    proveedor = servidor.proveedor()
    primera = obtener(proveedor)
    assert obtener(proveedor) == primera
    assert proveedor.circuito.fallos_consecutivos == 1


def test_sin_trm_previa_un_fallo_lanza_tasa_no_disponible():
    proveedor = Servidor(httpx.Response(503)).proveedor()
    with pytest.raises(TasaNoDisponibleError):
        obtener(proveedor)


def test_tres_fallos_abren_el_circuito_y_dejan_de_consultar():
    servidor = Servidor(ok(), httpx.Response(500), httpx.Response(500), httpx.ReadTimeout("x"))
    proveedor = servidor.proveedor()
    for _ in range(4):
        trm = obtener(proveedor)
    assert proveedor.circuito.estado == EstadoCircuito.ABIERTO
    assert len(servidor.peticiones) == 4
    assert obtener(proveedor) == trm
    assert len(servidor.peticiones) == 4


def test_se_recupera_cuando_pasan_60_segundos():
    reloj = [0.0]
    circuito = CircuitBreaker(reloj=lambda: reloj[0])
    servidor = Servidor(ok(), *[httpx.Response(500)] * 3, ok([{**RESPUESTA[0], "valor": "4300"}]))
    proveedor = servidor.proveedor(circuito=circuito)
    for _ in range(4):
        obtener(proveedor)
    reloj[0] = 60.0
    assert obtener(proveedor).valor == 4300.0
    assert circuito.estado == EstadoCircuito.CERRADO
