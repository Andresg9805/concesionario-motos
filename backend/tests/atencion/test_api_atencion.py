import re

import pytest

from app.api import dependencias
from app.domain.catalogo import PlanCredito
from app.infrastructure.memoria.usuarios import RepositorioUsuariosEnMemoria
from app.main import app
from tests.atencion.conftest import COTIZACION, MOTO_KAWASAKI, TEST_DRIVE

PATRON_CODIGO = r"^CM-[A-Z0-9]{4}$"


def test_crear_cotizacion_asigna_asesor_de_la_marca_y_codigo(cliente_http, clientes):
    respuesta = cliente_http.post("/cotizaciones", json=COTIZACION)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    cuota = PlanCredito(
        precio_cop=12_890_000, cuota_inicial_cop=1_289_000, plazo_meses=36, tasa_mensual=0.0179
    ).cuota_mensual()
    assert cuerpo == {
        "codigo": cuerpo["codigo"],
        "tipo": "COTIZACION",
        "estado": "NUEVO",
        "creada_en": "2026-11-13T20:00:00-05:00",
        "moto": {
            "id": 3,
            "modelo": "CB190R",
            "marca": {"id": 1, "nombre": "Honda", "clave": "honda", "color_hex": "#CC0000"},
        },
        "asesor": {"nombre": "Laura Ruiz", "whatsapp": "3001112233"},
        "cuota_mensual_cop": cuota,
    }
    assert re.match(PATRON_CODIGO, cuerpo["codigo"])
    assert clientes.buscar_por_correo("ana@correo.com").telefono == "3001234567"


def test_crear_test_drive_queda_pendiente_sin_cuota(cliente_http):
    respuesta = cliente_http.post("/test-drives", json=TEST_DRIVE)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["tipo"] == "TEST_DRIVE"
    assert cuerpo["estado"] == "PENDIENTE"
    assert cuerpo["cuota_mensual_cop"] is None
    assert cuerpo["asesor"]["nombre"] == "Laura Ruiz"


def test_el_cliente_se_reutiliza_por_correo(cliente_http, clientes):
    cliente_http.post("/cotizaciones", json=COTIZACION)
    cliente_http.post("/test-drives", json={**TEST_DRIVE, "correo": "ANA@correo.com"})

    assert clientes.buscar_por_correo("ana@correo.com").id == 1


@pytest.mark.parametrize(
    ("ruta", "cuerpo"), [("/cotizaciones", COTIZACION), ("/test-drives", TEST_DRIVE)]
)
def test_seguimiento_encuentra_la_atencion(cliente_http, ruta, cuerpo):
    creada = cliente_http.post(ruta, json=cuerpo).json()

    respuesta = cliente_http.get(f"/seguimiento/{creada['codigo'].lower()}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


@pytest.mark.parametrize("codigo", ["CM-ZZZZ", "CM-12", "XX-ABCD", "cm_abcd"])
def test_seguimiento_con_codigo_inexistente_o_malo_responde_404(cliente_http, codigo):
    assert cliente_http.get(f"/seguimiento/{codigo}").status_code == 404


@pytest.mark.parametrize("ruta", ["/cotizaciones", "/test-drives"])
def test_moto_inexistente_responde_404(cliente_http, ruta):
    respuesta = cliente_http.post(ruta, json={**TEST_DRIVE, "moto_id": 999})

    assert respuesta.status_code == 404


@pytest.mark.parametrize("ruta", ["/cotizaciones", "/test-drives"])
def test_sin_asesores_de_la_marca_responde_409(cliente_http, ruta):
    sin_asesores = RepositorioUsuariosEnMemoria()
    app.dependency_overrides[dependencias.obtener_repositorio_usuarios] = lambda: sin_asesores

    respuesta = cliente_http.post(ruta, json={**TEST_DRIVE, "moto_id": MOTO_KAWASAKI})

    assert respuesta.status_code == 409


@pytest.mark.parametrize(
    "cambio",
    [
        {"acepta_contacto": False},
        {"correo": "sin-arroba"},
        {"celular": "12345"},
        {"nombre": ""},
        {"plazo_meses": 3},
        {"cuota_inicial_cop": 20_000_000},
        {"rol": "ADMIN"},
    ],
)
def test_datos_invalidos_responden_422(cliente_http, cambio):
    respuesta = cliente_http.post("/cotizaciones", json={**COTIZACION, **cambio})

    assert respuesta.status_code == 422


def test_test_drive_no_acepta_datos_de_credito(cliente_http):
    respuesta = cliente_http.post("/test-drives", json={**TEST_DRIVE, "plazo_meses": 36})

    assert respuesta.status_code == 422


def test_se_asigna_el_asesor_con_menos_atenciones_abiertas(cliente_http, segunda_asesora_honda):
    primera = cliente_http.post("/cotizaciones", json=COTIZACION).json()
    segunda = cliente_http.post("/test-drives", json=TEST_DRIVE).json()
    tercera = cliente_http.post("/cotizaciones", json=COTIZACION).json()

    assert primera["asesor"]["nombre"] == "Laura Ruiz"
    assert segunda["asesor"]["nombre"] == "Sofía Gómez"
    assert tercera["asesor"]["nombre"] == "Laura Ruiz"


def test_los_codigos_no_se_repiten(cliente_http):
    codigos = {
        cliente_http.post("/cotizaciones", json=COTIZACION).json()["codigo"] for _ in range(30)
    }

    assert len(codigos) == 30
