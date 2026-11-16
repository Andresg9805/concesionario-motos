from tests.admin.test_seguridad_admin import MOTO


def test_crear_moto_calcula_la_licencia_a_partir_del_cilindraje(cliente_http, admin):
    respuesta = cliente_http.post("/admin/motos", json=MOTO, headers=admin)
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["categoria_licencia"] == "A2"
    assert cuerpo["modelo"] == "CB 190R"
    assert cuerpo["marca"]["nombre"] == "Honda"
    assert cliente_http.get(f"/motos/{cuerpo['id']}").status_code == 200


def test_una_moto_de_125_cc_o_menos_es_a1(cliente_http, admin):
    respuesta = cliente_http.post(
        "/admin/motos", json={**MOTO, "cilindraje_cc": 125}, headers=admin
    )
    assert respuesta.json()["categoria_licencia"] == "A1"


def test_el_esquema_no_acepta_la_licencia(cliente_http, admin):
    respuesta = cliente_http.post("/admin/motos", json={**MOTO, "licencia": "A1"}, headers=admin)
    assert respuesta.status_code == 422


def test_crear_moto_con_marca_inexistente_responde_404(cliente_http, admin):
    respuesta = cliente_http.post("/admin/motos", json={**MOTO, "marca_id": 99}, headers=admin)
    assert respuesta.status_code == 404


def test_crear_moto_con_datos_invalidos_responde_422(cliente_http, admin):
    respuesta = cliente_http.post("/admin/motos", json={**MOTO, "precio_cop": 0}, headers=admin)
    assert respuesta.status_code == 422
    respuesta = cliente_http.post("/admin/motos", json={**MOTO, "tipo": "ELECTRICA"}, headers=admin)
    assert respuesta.status_code == 422


def test_actualizar_moto_recalcula_la_licencia(cliente_http, admin):
    creada = cliente_http.post("/admin/motos", json=MOTO, headers=admin).json()
    respuesta = cliente_http.put(
        f"/admin/motos/{creada['id']}",
        json={**MOTO, "cilindraje_cc": 110, "precio_cop": 7_000_000},
        headers=admin,
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == creada["id"]
    assert respuesta.json()["categoria_licencia"] == "A1"
    assert respuesta.json()["precio_cop"] == 7_000_000


def test_actualizar_moto_inexistente_o_con_marca_inexistente_responde_404(cliente_http, admin):
    assert cliente_http.put("/admin/motos/9999", json=MOTO, headers=admin).status_code == 404
    respuesta = cliente_http.put("/admin/motos/1", json={**MOTO, "marca_id": 99}, headers=admin)
    assert respuesta.status_code == 404


def test_eliminar_moto(cliente_http, admin):
    creada = cliente_http.post("/admin/motos", json=MOTO, headers=admin).json()
    assert cliente_http.delete(f"/admin/motos/{creada['id']}", headers=admin).status_code == 204
    assert cliente_http.get(f"/motos/{creada['id']}").status_code == 404
    assert cliente_http.delete(f"/admin/motos/{creada['id']}", headers=admin).status_code == 404
