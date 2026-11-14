import hashlib

from tests.pedidos.conftest import (
    ANA,
    ASESORA,
    CASCO,
    CHAQUETA,
    CONFIGURACION_WOMPI,
    COSTO_ENVIO_BOGOTA,
    LUIS,
)

PRECIO_CASCO = 489_000
PRECIO_CHAQUETA = 559_000
TOTAL_DOS_CASCOS = 2 * PRECIO_CASCO + COSTO_ENVIO_BOGOTA


def stock_de(accesorios, accesorio_id):
    return accesorios.buscar_por_id(accesorio_id).stock


def test_crear_pedido_responde_201_con_total_reserva_y_datos_del_widget(
    crear_pedido, reloj, accesorios
):
    respuesta = crear_pedido()
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    referencia = f"CM-PED-1-{int(reloj.ahora.timestamp())}"
    firma = hashlib.sha256(
        f"{referencia}{TOTAL_DOS_CASCOS * 100}COP{CONFIGURACION_WOMPI.secreto_integridad}".encode()
    ).hexdigest()
    assert cuerpo == {
        "pedido_id": 1,
        "total_cop": TOTAL_DOS_CASCOS,
        "reservado_hasta": "2026-11-15T20:15:00-05:00",
        "wompi": {
            "llave_publica": CONFIGURACION_WOMPI.llave_publica,
            "referencia": referencia,
            "monto_centavos": TOTAL_DOS_CASCOS * 100,
            "moneda": "COP",
            "firma_integridad": firma,
        },
    }
    assert stock_de(accesorios, CASCO) == 10


def test_el_total_suma_todos_los_items_y_el_envio_del_departamento(crear_pedido):
    respuesta = crear_pedido(
        items=[
            {"accesorio_id": CASCO, "cantidad": 1},
            {"accesorio_id": CHAQUETA, "cantidad": 3},
        ]
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["total_cop"] == (
        PRECIO_CASCO + 3 * PRECIO_CHAQUETA + COSTO_ENVIO_BOGOTA
    )


def test_el_envio_depende_del_departamento_de_la_direccion(crear_pedido, crear_direccion):
    direccion_id = crear_direccion(
        departamento_codigo="05", municipio_codigo="05001", municipio_nombre="Medellín"
    )
    respuesta = crear_pedido(direccion_id=direccion_id)
    assert respuesta.json()["total_cop"] == 2 * PRECIO_CASCO + 15_000


def test_los_items_repetidos_se_suman_en_una_sola_linea(crear_pedido, cliente_http, token_de):
    crear_pedido(
        items=[{"accesorio_id": CASCO, "cantidad": 1}, {"accesorio_id": CASCO, "cantidad": 2}]
    )
    detalle = cliente_http.get("/mis-pedidos/1", headers=token_de(ANA)).json()
    assert [(i["accesorio_id"], i["cantidad"]) for i in detalle["items"]] == [(CASCO, 3)]


def test_sin_stock_responde_409_y_no_crea_pedido_ni_pago(
    crear_pedido, cliente_http, token_de, accesorios, pagos
):
    respuesta = crear_pedido(items=[{"accesorio_id": CASCO, "cantidad": 13}])
    assert respuesta.status_code == 409
    assert cliente_http.get("/mis-pedidos", headers=token_de(ANA)).json() == []
    assert pagos.buscar_por_pedido(1) is None
    assert stock_de(accesorios, CASCO) == 12


def test_un_accesorio_inexistente_responde_409(crear_pedido):
    respuesta = crear_pedido(items=[{"accesorio_id": 9999, "cantidad": 1}])
    assert respuesta.status_code == 409


def test_si_un_accesorio_falla_no_se_reserva_ninguno(crear_pedido, accesorios):
    respuesta = crear_pedido(
        items=[
            {"accesorio_id": CASCO, "cantidad": 2},
            {"accesorio_id": CHAQUETA, "cantidad": 10},
        ]
    )
    assert respuesta.status_code == 409
    assert stock_de(accesorios, CASCO) == 12
    assert stock_de(accesorios, CHAQUETA) == 9


def test_la_reserva_descuenta_stock_para_el_siguiente_cliente(crear_pedido):
    assert crear_pedido(items=[{"accesorio_id": CHAQUETA, "cantidad": 9}]).status_code == 201
    assert crear_pedido(LUIS, items=[{"accesorio_id": CHAQUETA, "cantidad": 1}]).status_code == 409


def test_direccion_inexistente_responde_404(cliente_http, token_de):
    respuesta = cliente_http.post(
        "/pedidos",
        json={"direccion_id": 77, "items": [{"accesorio_id": CASCO, "cantidad": 1}]},
        headers=token_de(ANA),
    )
    assert respuesta.status_code == 404


def test_direccion_de_otro_cliente_responde_404(
    cliente_http, token_de, crear_direccion, accesorios
):
    direccion_de_luis = crear_direccion(LUIS)
    respuesta = cliente_http.post(
        "/pedidos",
        json={"direccion_id": direccion_de_luis, "items": [{"accesorio_id": CASCO, "cantidad": 1}]},
        headers=token_de(ANA),
    )
    assert respuesta.status_code == 404
    assert stock_de(accesorios, CASCO) == 12


def test_los_cuerpos_invalidos_responden_422(cliente_http, token_de):
    for cuerpo in (
        {"direccion_id": 1, "items": []},
        {"direccion_id": 1, "items": [{"accesorio_id": 1, "cantidad": 0}]},
        {"direccion_id": 0, "items": [{"accesorio_id": 1, "cantidad": 1}]},
        {"direccion_id": 1, "items": [{"accesorio_id": 1, "cantidad": 1}], "total_cop": 1},
    ):
        assert cliente_http.post("/pedidos", json=cuerpo, headers=token_de(ANA)).status_code == 422


def test_solo_los_clientes_autenticados_crean_pedidos(cliente_http, token_de):
    cuerpo = {"direccion_id": 1, "items": [{"accesorio_id": 1, "cantidad": 1}]}
    assert cliente_http.post("/pedidos", json=cuerpo).status_code == 401
    assert cliente_http.post("/pedidos", json=cuerpo, headers=token_de(ASESORA)).status_code == 403


def test_un_pedido_sin_pagar_expira_a_los_15_minutos_y_libera_el_stock(
    crear_pedido, cliente_http, token_de, reloj, accesorios
):
    crear_pedido()
    reloj.avanzar(14)
    assert cliente_http.get("/mis-pedidos/1", headers=token_de(ANA)).json()["estado_pedido"] == (
        "PENDIENTE_PAGO"
    )
    reloj.avanzar(2)
    detalle = cliente_http.get("/mis-pedidos/1", headers=token_de(ANA)).json()
    assert detalle["estado_pedido"] == "EXPIRADO"
    assert stock_de(accesorios, CASCO) == 12


def test_listar_mis_pedidos_trae_solo_los_propios_del_mas_reciente_al_mas_antiguo(
    crear_pedido, cliente_http, token_de
):
    crear_pedido()
    crear_pedido(LUIS)
    crear_pedido(items=[{"accesorio_id": CHAQUETA, "cantidad": 1}])
    propios = cliente_http.get("/mis-pedidos", headers=token_de(ANA)).json()
    assert [p["pedido_id"] for p in propios] == [3, 1]
    assert propios[0]["estado_pago"] == "PENDIENTE"
    assert propios[0]["numero_guia"] is None
    ajenos = cliente_http.get("/mis-pedidos", headers=token_de(LUIS)).json()
    assert [p["pedido_id"] for p in ajenos] == [2]


def test_el_detalle_incluye_items_totales_y_estado(crear_pedido, cliente_http, token_de):
    crear_pedido()
    detalle = cliente_http.get("/mis-pedidos/1", headers=token_de(ANA)).json()
    assert detalle["items"] == [
        {
            "accesorio_id": CASCO,
            "nombre": "Casco integral ECE 22.06",
            "cantidad": 2,
            "precio_unitario_cop": PRECIO_CASCO,
            "subtotal_cop": 2 * PRECIO_CASCO,
        }
    ]
    assert detalle["subtotal_cop"] == 2 * PRECIO_CASCO
    assert detalle["costo_envio_cop"] == COSTO_ENVIO_BOGOTA
    assert detalle["total_cop"] == TOTAL_DOS_CASCOS
    assert detalle["estado_pedido"] == "PENDIENTE_PAGO"
    assert detalle["estado_pago"] == "PENDIENTE"
    assert detalle["eventos"] == []


def test_un_cliente_no_ve_el_detalle_ni_verifica_el_pago_de_otro(
    crear_pedido, cliente_http, token_de
):
    crear_pedido()
    assert cliente_http.get("/mis-pedidos/1", headers=token_de(LUIS)).status_code == 404
    verificacion = cliente_http.post(
        "/mis-pedidos/1/verificar-pago",
        json={"transaccion_id": "100-1-1"},
        headers=token_de(LUIS),
    )
    assert verificacion.status_code == 404
    assert cliente_http.get("/mis-pedidos/99", headers=token_de(ANA)).status_code == 404
