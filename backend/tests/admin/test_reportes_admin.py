from datetime import datetime

import pytest

from app.api import dependencias
from app.domain.catalogo import Busqueda, CategoriaLicencia, UsoMoto
from app.infrastructure.memoria.catalogo import RepositorioBusquedasEnMemoria
from app.main import app
from tests.admin.conftest import ASESORA, CLIENTE


@pytest.fixture
def busquedas(cliente_http):
    repositorio = RepositorioBusquedasEnMemoria()
    app.dependency_overrides[dependencias.obtener_repositorio_busquedas] = lambda: repositorio
    return repositorio


def test_radar_de_demanda_con_busquedas(cliente_http, admin, busquedas):
    for cuota in (250_000, 280_000):
        busquedas.guardar(
            Busqueda(
                fecha=datetime(2026, 11, 16, 9, 0),
                cuota_maxima_cop=cuota,
                cuota_inicial_cop=0,
                categoria_licencia=CategoriaLicencia.A2,
                uso=UsoMoto.TRABAJO,
                cantidad_resultados=0,
            )
        )

    respuesta = cliente_http.get("/reportes/demanda", headers=admin)

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["total_busquedas"] == 2
    assert cuerpo["filas"][0]["rango"] == "Menos de $300.000"
    assert cuerpo["filas"][0]["sin_resultados"] == 2
    assert cuerpo["filas"][0]["motos_en_stock"] >= 0


def test_reporte_de_ventas_cuenta_solo_pedidos_pagados(cliente_http, admin, pedido_pagado):
    pedido_pagado()

    respuesta = cliente_http.get("/reportes/ventas", headers=admin)

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["pedidos"] == 1
    assert cuerpo["ingresos_cop"] > 0
    assert cuerpo["mas_vendidos"][0]["unidades"] == 2
    assert cuerpo["por_categoria_y_semana"][0]["categoria"] == "CASCO"


def test_reporte_de_ventas_sin_pedidos(cliente_http, admin):
    cuerpo = cliente_http.get("/reportes/ventas", headers=admin).json()

    assert cuerpo == {
        "pedidos": 0,
        "ingresos_cop": 0,
        "ticket_promedio_cop": 0,
        "por_categoria_y_semana": [],
        "mas_vendidos": [],
    }


@pytest.mark.parametrize("ruta", ["/reportes/demanda", "/reportes/ventas"])
def test_los_reportes_son_solo_para_el_admin(cliente_http, token_de, ruta):
    assert cliente_http.get(ruta).status_code == 401
    assert cliente_http.get(ruta, headers=token_de(CLIENTE)).status_code == 403
    assert cliente_http.get(ruta, headers=token_de(ASESORA)).status_code == 403
