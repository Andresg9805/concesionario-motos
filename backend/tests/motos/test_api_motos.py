import pytest

from app.domain.catalogo import TipoMoto


def test_listar_marcas(cliente_http):
    respuesta = cliente_http.get("/marcas")
    assert respuesta.status_code == 200
    assert [marca["nombre"] for marca in respuesta.json()] == ["Honda", "Kawasaki", "Yamaha"]
    assert [marca["clave"] for marca in respuesta.json()] == ["honda", "kawasaki", "yamaha"]
    assert all(marca["color_hex"].startswith("#") for marca in respuesta.json())


def test_listar_motos_sin_filtros(cliente_http):
    respuesta = cliente_http.get("/motos")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 22
    assert "stock" not in cuerpo[0]
    assert "consumo_km_galon" not in cuerpo[0]


@pytest.mark.parametrize("tipo", [tipo.value for tipo in TipoMoto])
def test_listar_motos_por_tipo(cliente_http, tipo):
    respuesta = cliente_http.get("/motos", params={"tipo": tipo})
    assert respuesta.status_code == 200
    assert respuesta.json()
    assert {moto["tipo"] for moto in respuesta.json()} == {tipo}


@pytest.mark.parametrize("tipo", ["SCOOTER", "CALLE", "naked"])
def test_listar_motos_con_tipo_no_permitido_responde_422(cliente_http, tipo):
    assert cliente_http.get("/motos", params={"tipo": tipo}).status_code == 422


def test_listar_motos_por_marca_y_licencia(cliente_http):
    respuesta = cliente_http.get("/motos", params={"marca_id": 3, "licencia": "A1"})
    assert respuesta.status_code == 200
    assert [moto["modelo"] for moto in respuesta.json()] == ["XTZ 125"]


def test_listar_motos_por_rango_de_cilindraje_y_precio(cliente_http):
    respuesta = cliente_http.get(
        "/motos",
        params={
            "cilindraje_min": 250,
            "cilindraje_max": 400,
            "precio_min": 20_000_000,
            "precio_max": 33_000_000,
        },
    )
    assert respuesta.status_code == 200
    modelos = {moto["modelo"] for moto in respuesta.json()}
    assert modelos == {"XRE 300 Rally", "Versys-X 300", "Z400", "MT-03"}


@pytest.mark.parametrize(
    "consulta",
    [
        {"precio_min": 30_000_000, "precio_max": 10_000_000},
        {"cilindraje_min": 500, "cilindraje_max": 100},
        {"marca_id": 0},
        {"filtro_raro": 1},
    ],
)
def test_listar_motos_con_filtros_invalidos_responde_422(cliente_http, consulta):
    assert cliente_http.get("/motos", params=consulta).status_code == 422


def test_detalle_de_moto(cliente_http):
    respuesta = cliente_http.get("/motos/22")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["modelo"] == "MT-03"
    assert cuerpo["marca"]["nombre"] == "Yamaha"
    assert cuerpo["categoria_licencia"] == "A2"
    assert cuerpo["consumo_km_galon"] > 0
    assert "stock" not in cuerpo


def test_detalle_de_moto_inexistente_responde_404(cliente_http):
    respuesta = cliente_http.get("/motos/999")
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "No existe una moto con id 999"


def test_detalle_con_id_no_numerico_responde_422(cliente_http):
    assert cliente_http.get("/motos/abc").status_code == 422


def test_por_cuota_no_choca_con_la_ruta_del_detalle(cliente_http):
    respuesta = cliente_http.get("/motos/por-cuota", params={"cuota_maxima_cop": 400_000})
    assert respuesta.status_code == 200
    assert "precio_maximo_cop" in respuesta.json()


def test_por_cuota_con_licencia_a1(cliente_http):
    respuesta = cliente_http.get(
        "/motos/por-cuota",
        params={
            "cuota_maxima_cop": 350_000,
            "cuota_inicial_cop": 1_000_000,
            "plazo_meses": 36,
            "licencia": "A1",
        },
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["cantidad_resultados"] == len(cuerpo["motos"]) > 0
    assert all(item["moto"]["cilindraje_cc"] <= 125 for item in cuerpo["motos"])
    assert all(item["cuota_mensual_cop"] <= 350_000 for item in cuerpo["motos"])
    assert all(
        item["moto"]["precio_cop"] <= cuerpo["precio_maximo_cop"] for item in cuerpo["motos"]
    )


def test_por_cuota_guarda_busqueda_y_simulacion_de_la_sesion(cliente_http, busquedas, simulaciones):
    cabeceras = {"X-Sesion-Id": "sesion-demo-0001"}
    primera = cliente_http.get(
        "/motos/por-cuota", params={"cuota_maxima_cop": 300_000}, headers=cabeceras
    )
    segunda = cliente_http.get(
        "/motos/por-cuota",
        params={"cuota_maxima_cop": 600_000, "plazo_meses": 48},
        headers=cabeceras,
    )
    assert primera.json()["simulaciones_en_sesion"] == 1
    assert segunda.json()["simulaciones_en_sesion"] == 2
    assert segunda.json()["busqueda_id"] == 2
    assert segunda.headers["X-Sesion-Id"] == "sesion-demo-0001"
    assert len(busquedas.listar()) == 2
    assert simulaciones.ultima("sesion-demo-0001").plazo_meses == 48


def test_por_cuota_sin_sesion_crea_una(cliente_http, simulaciones):
    respuesta = cliente_http.get("/motos/por-cuota", params={"cuota_maxima_cop": 300_000})
    sesion = respuesta.json()["sesion_id"]
    assert respuesta.headers["X-Sesion-Id"] == sesion
    assert simulaciones.cantidad(sesion) == 1


@pytest.mark.parametrize(
    "consulta",
    [
        {},
        {"cuota_maxima_cop": 0},
        {"cuota_maxima_cop": 300_000, "plazo_meses": 0},
        {"cuota_maxima_cop": 300_000, "plazo_meses": 120},
        {"cuota_maxima_cop": 300_000, "cuota_inicial_cop": -1},
        {"cuota_maxima_cop": 300_000, "licencia": "B1"},
    ],
)
def test_por_cuota_con_datos_invalidos_responde_422(cliente_http, busquedas, consulta):
    assert cliente_http.get("/motos/por-cuota", params=consulta).status_code == 422
    assert busquedas.listar() == []


def test_por_cuota_con_sesion_invalida_responde_422(cliente_http):
    respuesta = cliente_http.get(
        "/motos/por-cuota",
        params={"cuota_maxima_cop": 300_000},
        headers={"X-Sesion-Id": "x"},
    )
    assert respuesta.status_code == 422


def test_costo_real(cliente_http):
    respuesta = cliente_http.get(
        "/motos/14/costo-real",
        params={"km_mes": 800, "uso": "CIUDAD", "cuota_inicial_cop": 5_000_000, "plazo_meses": 24},
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    adquisicion = cuerpo["adquisicion"]
    assert adquisicion["precio_lista_cop"] == 35_990_000
    assert adquisicion["total_cop"] == sum(
        adquisicion[campo]
        for campo in (
            "precio_lista_cop",
            "matricula_cop",
            "soat_cop",
            "impuesto_cop",
            "tramites_cop",
        )
    )
    mensual = cuerpo["mensual"]
    assert mensual["total_cop"] == sum(
        mensual[campo]
        for campo in (
            "cuota_credito_cop",
            "gasolina_cop",
            "soat_cop",
            "mantenimiento_cop",
            "impuesto_cop",
        )
    )
    assert cuerpo["financiacion"]["monto_financiado_cop"] == 30_990_000
    assert cuerpo["financiacion"]["cuota_mensual_cop"] == mensual["cuota_credito_cop"]
    assert cuerpo["modo_trabajo"] is None


def test_costo_real_en_modo_trabajo(cliente_http):
    respuesta = cliente_http.get(
        "/motos/1/costo-real",
        params={"uso": "TRABAJO", "ganancia_diaria_cop": 80_000, "dias_trabajo_mes": 26},
    )
    assert respuesta.status_code == 200
    trabajo = respuesta.json()["modo_trabajo"]
    assert trabajo["ganancia_mensual_cop"] == 2_080_000
    assert trabajo["meses_para_pagarse"] > 0


def test_costo_real_de_moto_inexistente_responde_404(cliente_http):
    respuesta = cliente_http.get("/motos/999/costo-real")
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "No existe una moto con id 999"


@pytest.mark.parametrize(
    "consulta",
    [
        {"cuota_inicial_cop": 99_000_000},
        {"km_mes": -5},
        {"uso": "PASEO"},
        {"ganancia_diaria_cop": 80_000},
    ],
)
def test_costo_real_con_datos_invalidos_responde_422(cliente_http, consulta):
    assert cliente_http.get("/motos/1/costo-real", params=consulta).status_code == 422
