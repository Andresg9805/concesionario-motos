import pytest

from tests.pedidos.conftest import (
    ANA,
    CASCO,
    COSTO_ENVIO_BOGOTA,
    LUIS,
    evento_firmado,
    transaccion,
)

TOTAL = 2 * 489_000 + COSTO_ENVIO_BOGOTA
ID_TRANSACCION = "12345-1731700000-12345"


@pytest.fixture
def pedido_creado(crear_pedido):
    respuesta = crear_pedido()
    assert respuesta.status_code == 201
    return respuesta.json()


def verificar(cliente_http, token_de, correo=ANA, pedido_id=1, transaccion_id=ID_TRANSACCION):
    return cliente_http.post(
        f"/mis-pedidos/{pedido_id}/verificar-pago",
        json={"transaccion_id": transaccion_id},
        headers=token_de(correo),
    )


def webhook(cliente_http, cuerpo, ruta="/webhooks/wompi"):
    return cliente_http.post(ruta, json=cuerpo)


def test_pago_aprobado_deja_el_pedido_pagado_y_crea_el_envio_con_guia(
    cliente_http, token_de, transporte, pedido_creado, envios
):
    referencia = pedido_creado["wompi"]["referencia"]
    transporte.registrar(ID_TRANSACCION, referencia, "APPROVED", TOTAL)
    respuesta = verificar(cliente_http, token_de)
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "pedido_id": 1,
        "estado_pago": "APROBADO",
        "estado_pedido": "PAGADO",
        "total_cop": TOTAL,
        "numero_guia": "CM-ENV-000001",
        "reservado_hasta": None,
    }
    assert transporte.consultas == [f"https://sandbox.wompi.test/v1/transactions/{ID_TRANSACCION}"]
    assert len(envios.listar()) == 1


def test_el_detalle_del_pedido_pagado_trae_guia_y_eventos_del_envio(
    cliente_http, token_de, transporte, pedido_creado, reloj
):
    transporte.registrar(ID_TRANSACCION, pedido_creado["wompi"]["referencia"], "APPROVED", TOTAL)
    verificar(cliente_http, token_de)
    detalle = cliente_http.get("/mis-pedidos/1", headers=token_de(ANA)).json()
    assert detalle["estado_pedido"] == "PAGADO"
    assert detalle["estado_pago"] == "APROBADO"
    assert detalle["numero_guia"] == "CM-ENV-000001"
    assert detalle["reservado_hasta"] is None
    assert detalle["estado_envio"] == "PREPARANDO"
    assert detalle["eventos"] == [
        {"estado": "PREPARANDO", "fecha": "2026-11-15T20:00:00-05:00", "nota": "Pago aprobado"}
    ]


def test_pago_rechazado_no_paga_ni_crea_envio_y_mantiene_la_reserva(
    cliente_http, token_de, transporte, pedido_creado, envios
):
    transporte.registrar(ID_TRANSACCION, pedido_creado["wompi"]["referencia"], "DECLINED", TOTAL)
    respuesta = verificar(cliente_http, token_de)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado_pago"] == "RECHAZADO"
    assert cuerpo["estado_pedido"] == "PENDIENTE_PAGO"
    assert cuerpo["numero_guia"] is None
    assert cuerpo["reservado_hasta"] == pedido_creado["reservado_hasta"]
    assert envios.listar() == []


def test_pago_pendiente_no_cambia_nada(cliente_http, token_de, transporte, pedido_creado, envios):
    transporte.registrar(ID_TRANSACCION, pedido_creado["wompi"]["referencia"], "PENDING", TOTAL)
    cuerpo = verificar(cliente_http, token_de).json()
    assert cuerpo["estado_pago"] == "PENDIENTE"
    assert cuerpo["estado_pedido"] == "PENDIENTE_PAGO"
    assert cuerpo["numero_guia"] is None
    assert envios.listar() == []


def test_pago_con_error_queda_en_error(cliente_http, token_de, transporte, pedido_creado):
    transporte.registrar(ID_TRANSACCION, pedido_creado["wompi"]["referencia"], "ERROR", TOTAL)
    cuerpo = verificar(cliente_http, token_de).json()
    assert cuerpo["estado_pago"] == "ERROR"
    assert cuerpo["estado_pedido"] == "PENDIENTE_PAGO"


def test_sin_transaccion_id_el_pago_sigue_pendiente_y_no_consulta_a_wompi(
    cliente_http, token_de, transporte, pedido_creado
):
    respuesta = verificar(cliente_http, token_de, transaccion_id=None)
    assert respuesta.status_code == 200
    assert respuesta.json()["estado_pago"] == "PENDIENTE"
    assert transporte.consultas == []


def test_verificar_dos_veces_un_pago_aprobado_no_duplica_el_envio(
    cliente_http, token_de, transporte, pedido_creado, envios
):
    transporte.registrar(ID_TRANSACCION, pedido_creado["wompi"]["referencia"], "APPROVED", TOTAL)
    verificar(cliente_http, token_de)
    segunda = verificar(cliente_http, token_de)
    assert segunda.status_code == 200
    assert segunda.json()["numero_guia"] == "CM-ENV-000001"
    assert len(envios.listar()) == 1


def test_una_transaccion_de_otra_referencia_responde_422(
    cliente_http, token_de, transporte, pedido_creado, envios
):
    transporte.registrar(ID_TRANSACCION, "CM-PED-99-1", "APPROVED", TOTAL)
    assert verificar(cliente_http, token_de).status_code == 422
    assert envios.listar() == []


def test_una_transaccion_con_otro_monto_responde_422(
    cliente_http, token_de, transporte, pedido_creado
):
    transporte.registrar(ID_TRANSACCION, pedido_creado["wompi"]["referencia"], "APPROVED", 1_000)
    assert verificar(cliente_http, token_de).status_code == 422


def test_si_wompi_no_responde_se_devuelve_502_y_el_pago_sigue_pendiente(
    cliente_http, token_de, transporte, pedido_creado, pagos
):
    transporte.caido = True
    assert verificar(cliente_http, token_de).status_code == 502
    assert pagos.buscar_por_pedido(1).estado.value == "PENDIENTE"


def test_el_identificador_de_transaccion_no_admite_caracteres_de_ruta(
    cliente_http, token_de, pedido_creado, transporte
):
    respuesta = verificar(cliente_http, token_de, transaccion_id="../merchants/pub")
    assert respuesta.status_code == 422
    assert transporte.consultas == []


def test_un_cliente_no_puede_verificar_el_pago_de_otro(
    cliente_http, token_de, transporte, pedido_creado, envios
):
    transporte.registrar(ID_TRANSACCION, pedido_creado["wompi"]["referencia"], "APPROVED", TOTAL)
    assert verificar(cliente_http, token_de, correo=LUIS).status_code == 404
    assert transporte.consultas == []
    assert envios.listar() == []


def test_webhook_con_checksum_invalido_responde_401_y_no_cambia_nada(
    cliente_http, transporte, pedido_creado, pagos, envios
):
    evento = evento_firmado(
        transaccion("t-1", pedido_creado["wompi"]["referencia"], "APPROVED", TOTAL * 100 // 100),
        secreto="otro_secreto",
    )
    assert webhook(cliente_http, evento).status_code == 401
    assert pagos.buscar_por_pedido(1).estado.value == "PENDIENTE"
    assert envios.listar() == []


def test_webhook_manipulado_despues_de_firmado_responde_401(cliente_http, pedido_creado):
    evento = evento_firmado(
        transaccion("t-1", pedido_creado["wompi"]["referencia"], "DECLINED", TOTAL)
    )
    evento["data"]["transaction"]["status"] = "APPROVED"
    assert webhook(cliente_http, evento).status_code == 401


@pytest.mark.parametrize(
    "cuerpo",
    [
        {},
        {"event": "transaction.updated", "data": {}},
        {"event": "transaction.updated", "data": {}, "signature": {"checksum": "abc"}},
        {
            "event": "transaction.updated",
            "data": {},
            "signature": {"properties": [], "checksum": "a"},
        },
        {
            "event": "transaction.updated",
            "data": {},
            "timestamp": 1,
            "signature": {"properties": ["transaction.id"], "checksum": "abc"},
        },
    ],
)
def test_webhook_sin_firma_o_incompleto_responde_401(cliente_http, cuerpo):
    assert webhook(cliente_http, cuerpo).status_code == 401


def test_webhook_aprobado_actualiza_el_pago_marca_pagado_y_crea_el_envio(
    cliente_http, token_de, pedido_creado, pagos, envios
):
    evento = evento_firmado(
        transaccion("t-1", pedido_creado["wompi"]["referencia"], "APPROVED", TOTAL)
    )
    respuesta = webhook(cliente_http, evento)
    assert respuesta.status_code == 200
    assert respuesta.json() == {"procesado": True}
    assert pagos.buscar_por_pedido(1).estado.value == "APROBADO"
    assert pagos.buscar_por_pedido(1).transaccion_id == "t-1"
    detalle = cliente_http.get("/mis-pedidos/1", headers=token_de(ANA)).json()
    assert detalle["estado_pedido"] == "PAGADO"
    assert detalle["numero_guia"] == "CM-ENV-000001"
    assert len(envios.listar()) == 1


def test_webhook_repetido_responde_200_sin_duplicar_ni_cambiar_nada_rn_09(
    cliente_http, pedido_creado, pagos, envios, pedidos
):
    evento = evento_firmado(
        transaccion("t-1", pedido_creado["wompi"]["referencia"], "APPROVED", TOTAL)
    )
    primera = webhook(cliente_http, evento)
    guia = envios.buscar_por_pedido(1).numero_guia
    eventos_del_envio = list(envios.buscar_por_pedido(1).eventos)
    segunda = webhook(cliente_http, evento)
    assert primera.status_code == segunda.status_code == 200
    assert primera.json() == {"procesado": True}
    assert segunda.json() == {"procesado": False}
    assert len(envios.listar()) == 1
    assert envios.buscar_por_pedido(1).numero_guia == guia
    assert envios.buscar_por_pedido(1).eventos == eventos_del_envio
    assert pedidos.buscar_por_id(1).estado.value == "PAGADO"


def test_webhook_rechazado_actualiza_el_pago_sin_pagar_el_pedido(
    cliente_http, pedido_creado, pagos, pedidos, envios
):
    evento = evento_firmado(
        transaccion("t-1", pedido_creado["wompi"]["referencia"], "DECLINED", TOTAL)
    )
    assert webhook(cliente_http, evento).status_code == 200
    assert pagos.buscar_por_pedido(1).estado.value == "RECHAZADO"
    assert pedidos.buscar_por_id(1).estado.value == "PENDIENTE_PAGO"
    assert envios.listar() == []


def test_webhook_y_verificacion_juntos_crean_un_solo_envio(
    cliente_http, token_de, transporte, pedido_creado, envios
):
    referencia = pedido_creado["wompi"]["referencia"]
    webhook(cliente_http, evento_firmado(transaccion("t-1", referencia, "APPROVED", TOTAL)))
    transporte.registrar("t-1", referencia, "APPROVED", TOTAL)
    respuesta = verificar(cliente_http, token_de, transaccion_id="t-1")
    assert respuesta.status_code == 200
    assert respuesta.json()["numero_guia"] == "CM-ENV-000001"
    assert len(envios.listar()) == 1


def test_webhook_de_una_referencia_desconocida_responde_404(cliente_http, pedido_creado):
    evento = evento_firmado(transaccion("t-1", "CM-PED-99-1", "APPROVED", TOTAL))
    assert webhook(cliente_http, evento).status_code == 404


def test_webhook_con_otro_monto_responde_422_y_no_paga(
    cliente_http, pedido_creado, pedidos, envios
):
    evento = evento_firmado(transaccion("t-1", pedido_creado["wompi"]["referencia"], "APPROVED", 5))
    assert webhook(cliente_http, evento).status_code == 422
    assert pedidos.buscar_por_id(1).estado.value == "PENDIENTE_PAGO"
    assert envios.listar() == []


def test_webhook_de_otro_tipo_de_evento_se_ignora_con_200(cliente_http, pedido_creado):
    evento = evento_firmado(
        transaccion("t-1", pedido_creado["wompi"]["referencia"], "APPROVED", TOTAL)
    )
    evento["event"] = "nequi_token.updated"
    assert webhook(cliente_http, evento).json() == {"procesado": False}


def test_la_ruta_alias_pagos_webhook_funciona_igual(cliente_http, pedido_creado, envios):
    evento = evento_firmado(
        transaccion("t-1", pedido_creado["wompi"]["referencia"], "APPROVED", TOTAL)
    )
    assert webhook(cliente_http, evento, ruta="/pagos/webhook").status_code == 200
    assert len(envios.listar()) == 1


def test_un_pedido_expirado_no_se_paga_con_un_aviso_tardio(
    cliente_http, token_de, pedido_creado, reloj, envios, accesorios
):
    reloj.avanzar(16)
    assert cliente_http.get("/mis-pedidos", headers=token_de(ANA)).json()[0]["estado_pedido"] == (
        "EXPIRADO"
    )
    evento = evento_firmado(
        transaccion("t-1", pedido_creado["wompi"]["referencia"], "APPROVED", TOTAL)
    )
    assert webhook(cliente_http, evento).status_code == 200
    assert envios.listar() == []
    assert accesorios.buscar_por_id(CASCO).stock == 12
