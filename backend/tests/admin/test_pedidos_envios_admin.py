import pytest

from tests.admin.conftest import CLIENTE
from tests.pedidos.conftest import COSTO_ENVIO_BOGOTA

TOTAL = 2 * 489_000 + COSTO_ENVIO_BOGOTA


def test_listado_de_pedidos_vacio(cliente_http, admin):
    respuesta = cliente_http.get("/admin/pedidos", headers=admin)
    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listado_de_pedidos_incluye_estado_total_y_envio(cliente_http, admin, pedido_pagado):
    pedido_id = pedido_pagado()
    respuesta = cliente_http.get("/admin/pedidos", headers=admin)
    assert respuesta.status_code == 200
    [pedido] = respuesta.json()
    assert pedido["id"] == pedido_id
    assert pedido["cliente_correo"] == CLIENTE
    assert pedido["estado"] == "PAGADO"
    assert pedido["estado_pago"] == "APROBADO"
    assert pedido["total_cop"] == TOTAL
    assert pedido["items"][0]["cantidad"] == 2
    assert pedido["envio"]["estado"] == "PREPARANDO"
    assert pedido["envio"]["numero_guia"].startswith("CM-ENV-")
    assert [e["estado"] for e in pedido["envio"]["eventos"]] == ["PREPARANDO"]


def test_un_pedido_sin_pagar_aparece_sin_envio(cliente_http, admin, token_de):
    direccion = cliente_http.post(
        "/mis-direcciones",
        json={
            "nombre_recibe": "Ana Pérez",
            "telefono": "3001234567",
            "departamento_codigo": "11",
            "municipio_codigo": "11001",
            "municipio_nombre": "Bogotá D.C.",
            "direccion": "Calle 26 # 13-19",
        },
        headers=token_de(CLIENTE),
    ).json()["id"]
    cliente_http.post(
        "/pedidos",
        json={"direccion_id": direccion, "items": [{"accesorio_id": 1, "cantidad": 1}]},
        headers=token_de(CLIENTE),
    )
    [pedido] = cliente_http.get("/admin/pedidos", headers=admin).json()
    assert pedido["estado"] == "PENDIENTE_PAGO"
    assert pedido["estado_pago"] == "PENDIENTE"
    assert pedido["envio"] is None


def test_el_envio_avanza_paso_a_paso_hasta_entregado(cliente_http, admin, pedido_pagado):
    pedido_pagado()
    [pedido] = cliente_http.get("/admin/pedidos", headers=admin).json()
    envio_id = pedido["envio"]["id"]
    for estado in ("ENVIADO", "EN_CAMINO", "ENTREGADO"):
        respuesta = cliente_http.patch(
            f"/envios/{envio_id}/estado", json={"estado": estado, "nota": "avance"}, headers=admin
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["estado"] == estado
    eventos = respuesta.json()["eventos"]
    assert [e["estado"] for e in eventos] == ["PREPARANDO", "ENVIADO", "EN_CAMINO", "ENTREGADO"]
    assert eventos[-1]["nota"] == "avance"


@pytest.mark.parametrize("estado", ["EN_CAMINO", "ENTREGADO", "PREPARANDO"])
def test_no_se_puede_saltar_ni_repetir_un_estado(cliente_http, admin, pedido_pagado, estado):
    pedido_pagado()
    respuesta = cliente_http.patch("/envios/1/estado", json={"estado": estado}, headers=admin)
    assert respuesta.status_code == 422


def test_no_se_puede_retroceder_un_estado(cliente_http, admin, pedido_pagado):
    pedido_pagado()
    cliente_http.patch("/envios/1/estado", json={"estado": "ENVIADO"}, headers=admin)
    respuesta = cliente_http.patch("/envios/1/estado", json={"estado": "PREPARANDO"}, headers=admin)
    assert respuesta.status_code == 422
    envio = cliente_http.get("/admin/pedidos", headers=admin).json()[0]["envio"]
    assert envio["estado"] == "ENVIADO"


def test_no_se_avanza_un_envio_entregado(cliente_http, admin, pedido_pagado):
    pedido_pagado()
    for estado in ("ENVIADO", "EN_CAMINO", "ENTREGADO"):
        cliente_http.patch("/envios/1/estado", json={"estado": estado}, headers=admin)
    respuesta = cliente_http.patch("/envios/1/estado", json={"estado": "ENTREGADO"}, headers=admin)
    assert respuesta.status_code == 422


def test_envio_inexistente_responde_404(cliente_http, admin):
    respuesta = cliente_http.patch("/envios/99/estado", json={"estado": "ENVIADO"}, headers=admin)
    assert respuesta.status_code == 404


def test_estado_de_envio_invalido_responde_422(cliente_http, admin, pedido_pagado):
    pedido_pagado()
    respuesta = cliente_http.patch("/envios/1/estado", json={"estado": "PERDIDO"}, headers=admin)
    assert respuesta.status_code == 422


def test_el_cliente_ve_el_avance_del_envio_en_su_pedido(
    cliente_http, admin, token_de, pedido_pagado
):
    pedido_id = pedido_pagado()
    cliente_http.patch("/envios/1/estado", json={"estado": "ENVIADO"}, headers=admin)
    detalle = cliente_http.get(f"/mis-pedidos/{pedido_id}", headers=token_de(CLIENTE)).json()
    assert detalle["estado_envio"] == "ENVIADO"
