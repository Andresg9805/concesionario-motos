import pytest

from tests.admin.test_seguridad_admin import PARAMETROS


def test_consultar_parametros_de_costo(cliente_http, admin):
    respuesta = cliente_http.get("/parametros-costo", headers=admin)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["precio_galon_cop"] == 16_200
    assert cuerpo["porcentaje_impuesto"] == 1.5
    assert len(cuerpo["tarifas_soat"]) == 3


def test_actualizar_parametros_cambia_el_costo_real(cliente_http, admin):
    antes = cliente_http.get("/motos/20/costo-real").json()
    respuesta = cliente_http.put("/parametros-costo", json=PARAMETROS, headers=admin)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["precio_galon_cop"] == 17_000
    assert cuerpo["porcentaje_impuesto"] == 2.0
    assert cuerpo["tarifas_soat"][0]["valor_anual_cop"] == 300_000
    assert cuerpo["valor_matricula_cop"] == 520_000
    assert cliente_http.get("/parametros-costo", headers=admin).json() == cuerpo
    assert cliente_http.get("/motos/20/costo-real").json() != antes


def test_actualizar_parametros_acepta_matricula_tramites_y_tasa(cliente_http, admin):
    cambios = {"valor_matricula_cop": 600_000, "valor_tramites_cop": 400_000, "tasa_mensual": 0.02}
    respuesta = cliente_http.put("/parametros-costo", json={**PARAMETROS, **cambios}, headers=admin)
    assert respuesta.status_code == 200
    assert respuesta.json()["valor_matricula_cop"] == 600_000
    assert respuesta.json()["tasa_mensual"] == 0.02


@pytest.mark.parametrize(
    "cambio",
    [
        {"precio_galon_cop": 0},
        {"porcentaje_impuesto": 101},
        {"porcentaje_impuesto": -1},
        {"tarifas_soat": []},
        {"tarifas_soat": [{"cilindraje_min": 50, "cilindraje_max": 10, "valor_anual_cop": 1}]},
        {"tasa_mensual": 1},
    ],
)
def test_parametros_invalidos_responden_422(cliente_http, admin, cambio):
    respuesta = cliente_http.put("/parametros-costo", json={**PARAMETROS, **cambio}, headers=admin)
    assert respuesta.status_code == 422
