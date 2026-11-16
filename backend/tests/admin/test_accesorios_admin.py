import pytest

from tests.admin.test_seguridad_admin import ACCESORIO


def test_crud_completo_de_accesorios(cliente_http, admin):
    creado = cliente_http.post("/admin/accesorios", json=ACCESORIO, headers=admin)
    assert creado.status_code == 201
    cuerpo = creado.json()
    assert cuerpo["categoria"] == "CASCO"
    assert cuerpo["fabricante"] == "Shaft"
    assert cliente_http.get(f"/accesorios/{cuerpo['id']}").status_code == 200

    actualizado = cliente_http.put(
        f"/admin/accesorios/{cuerpo['id']}",
        json={**ACCESORIO, "categoria": "GUANTES", "fabricante": "Alpinestars", "stock": 9},
        headers=admin,
    )
    assert actualizado.status_code == 200
    assert actualizado.json()["categoria"] == "GUANTES"
    assert actualizado.json()["fabricante"] == "Alpinestars"
    assert actualizado.json()["stock"] == 9

    assert (
        cliente_http.delete(f"/admin/accesorios/{cuerpo['id']}", headers=admin).status_code == 204
    )
    assert cliente_http.get(f"/accesorios/{cuerpo['id']}").status_code == 404


@pytest.mark.parametrize(
    "cambio",
    [
        {"categoria": "SOMBRERO"},
        {"fabricante": ""},
        {"precio_cop": 0},
        {"stock": -1},
        {"sku": "x"},
    ],
)
def test_accesorio_con_datos_invalidos_responde_422(cliente_http, admin, cambio):
    respuesta = cliente_http.post("/admin/accesorios", json={**ACCESORIO, **cambio}, headers=admin)
    assert respuesta.status_code == 422


def test_el_fabricante_es_obligatorio(cliente_http, admin):
    cuerpo = {clave: valor for clave, valor in ACCESORIO.items() if clave != "fabricante"}
    assert cliente_http.post("/admin/accesorios", json=cuerpo, headers=admin).status_code == 422


def test_accesorio_inexistente_responde_404(cliente_http, admin):
    assert (
        cliente_http.put("/admin/accesorios/9999", json=ACCESORIO, headers=admin).status_code == 404
    )
    assert cliente_http.delete("/admin/accesorios/9999", headers=admin).status_code == 404
