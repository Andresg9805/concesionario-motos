import pytest

from tests.admin.conftest import ASESORA, CLIENTE

MOTO = {
    "marca_id": 1,
    "modelo": "CB 190R",
    "anio": 2026,
    "cilindraje_cc": 184,
    "tipo": "NAKED",
    "precio_cop": 10_990_000,
    "stock": 3,
    "consumo_km_galon": 120.0,
    "costo_mantenimiento_km_cop": 95,
}
ACCESORIO = {
    "sku": "CAS-900",
    "nombre": "Casco modular",
    "categoria": "CASCO",
    "fabricante": "Shaft",
    "precio_cop": 500_000,
    "stock": 4,
}
PARAMETROS = {
    "precio_galon_cop": 17_000,
    "porcentaje_impuesto": 2.0,
    "tarifas_soat": [{"cilindraje_min": 0, "cilindraje_max": 100_000, "valor_anual_cop": 300_000}],
}

ENDPOINTS = [
    ("post", "/admin/motos", MOTO),
    ("put", "/admin/motos/1", MOTO),
    ("delete", "/admin/motos/1", None),
    ("post", "/admin/accesorios", ACCESORIO),
    ("put", "/admin/accesorios/1", ACCESORIO),
    ("delete", "/admin/accesorios/1", None),
    ("get", "/parametros-costo", None),
    ("put", "/parametros-costo", PARAMETROS),
    ("get", "/admin/pedidos", None),
    ("patch", "/envios/1/estado", {"estado": "ENVIADO"}),
    ("get", "/reportes/demanda", None),
    ("get", "/reportes/ventas", None),
]


def llamar(cliente_http, metodo, ruta, cuerpo, headers=None):
    return cliente_http.request(metodo, ruta, json=cuerpo, headers=headers or {})


@pytest.mark.parametrize(("metodo", "ruta", "cuerpo"), ENDPOINTS)
def test_sin_token_responde_401(cliente_http, metodo, ruta, cuerpo):
    assert llamar(cliente_http, metodo, ruta, cuerpo).status_code == 401


@pytest.mark.parametrize("correo", [CLIENTE, ASESORA])
@pytest.mark.parametrize(("metodo", "ruta", "cuerpo"), ENDPOINTS)
def test_cliente_y_asesor_reciben_403(cliente_http, token_de, correo, metodo, ruta, cuerpo):
    respuesta = llamar(cliente_http, metodo, ruta, cuerpo, token_de(correo))
    assert respuesta.status_code == 403


def test_el_administrador_accede_a_los_listados(cliente_http, admin):
    assert cliente_http.get("/parametros-costo", headers=admin).status_code == 200
    assert cliente_http.get("/admin/pedidos", headers=admin).status_code == 200


@pytest.mark.parametrize("ruta", ["/reportes/demanda", "/reportes/ventas"])
def test_los_reportes_del_administrador_responden_501_hasta_integrar_duckdb(
    cliente_http, admin, ruta
):
    assert cliente_http.get(ruta, headers=admin).status_code == 501
