import pytest

from app.domain.atencion import Rol, Usuario
from tests.atencion.conftest import COTIZACION, MOTO_KAWASAKI, TEST_DRIVE

LAURA = "laura.ruiz@candela.com"
CAMILO = "camilo.torres@candela.com"


def crear_cotizacion(cliente_http, **cambios):
    return cliente_http.post("/cotizaciones", json={**COTIZACION, **cambios}).json()


def id_de(cliente_http, token_de, codigo, correo=LAURA):
    atenciones = cliente_http.get("/asesor/atenciones", headers=token_de(correo)).json()
    return next(a["id"] for a in atenciones if a["codigo"] == codigo)


def test_el_panel_exige_sesion_de_asesor(cliente_http):
    assert cliente_http.get("/asesor/atenciones").status_code == 401
    assert cliente_http.get("/asesor/test-drives").status_code == 401


def test_un_cliente_no_entra_al_panel(cliente_http, usuarios, emisor):
    cliente = usuarios.guardar(
        Usuario(nombre="Ana", correo="ana@correo.com", hash_contrasena="hash", rol=Rol.CLIENTE)
    )
    cabecera = {"Authorization": f"Bearer {emisor.emitir(cliente)}"}

    assert cliente_http.get("/asesor/atenciones", headers=cabecera).status_code == 403


def test_el_asesor_ve_solo_sus_atenciones_con_el_contacto(cliente_http, token_de):
    honda = crear_cotizacion(cliente_http)
    crear_cotizacion(cliente_http, moto_id=MOTO_KAWASAKI)

    respuesta = cliente_http.get("/asesor/atenciones", headers=token_de(LAURA))

    assert respuesta.status_code == 200
    atenciones = respuesta.json()
    assert [a["codigo"] for a in atenciones] == [honda["codigo"]]
    assert atenciones[0]["id"] == 1
    assert atenciones[0]["cliente"] == {
        "nombre": "Ana Pérez",
        "correo": "ana@correo.com",
        "celular": "3001234567",
    }


def test_el_asesor_cambia_el_estado_de_su_cotizacion(cliente_http, token_de):
    cotizacion = crear_cotizacion(cliente_http)
    cotizacion_id = id_de(cliente_http, token_de, cotizacion["codigo"])

    respuesta = cliente_http.patch(
        f"/cotizaciones/{cotizacion_id}/estado",
        json={"estado": "CONTACTADO"},
        headers=token_de(LAURA),
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "CONTACTADO"
    seguimiento = cliente_http.get(f"/seguimiento/{cotizacion['codigo']}").json()
    assert seguimiento["estado"] == "CONTACTADO"


def test_un_asesor_no_cambia_la_cotizacion_de_otro(cliente_http, token_de):
    cotizacion = crear_cotizacion(cliente_http)
    cotizacion_id = id_de(cliente_http, token_de, cotizacion["codigo"])

    respuesta = cliente_http.patch(
        f"/cotizaciones/{cotizacion_id}/estado",
        json={"estado": "CONTACTADO"},
        headers=token_de(CAMILO),
    )

    assert respuesta.status_code == 403
    assert cliente_http.get(f"/seguimiento/{cotizacion['codigo']}").json()["estado"] == "NUEVO"


def test_transicion_invalida_responde_409(cliente_http, token_de):
    cotizacion = crear_cotizacion(cliente_http)
    cotizacion_id = id_de(cliente_http, token_de, cotizacion["codigo"])

    respuesta = cliente_http.patch(
        f"/cotizaciones/{cotizacion_id}/estado",
        json={"estado": "VENDIDO"},
        headers=token_de(LAURA),
    )

    assert respuesta.status_code == 409


@pytest.mark.parametrize(
    ("cotizacion_id", "estado", "esperado"),
    [(99, "CONTACTADO", 404), (1, "INVENTADO", 422)],
)
def test_cambio_de_estado_con_datos_malos(cliente_http, token_de, cotizacion_id, estado, esperado):
    crear_cotizacion(cliente_http)

    respuesta = cliente_http.patch(
        f"/cotizaciones/{cotizacion_id}/estado", json={"estado": estado}, headers=token_de(LAURA)
    )

    assert respuesta.status_code == esperado


def test_la_cola_de_test_drives_va_en_orden_de_llegada(cliente_http, token_de):
    primero = cliente_http.post("/test-drives", json=TEST_DRIVE).json()
    segundo = cliente_http.post(
        "/test-drives", json={**TEST_DRIVE, "correo": "luis@correo.com"}
    ).json()
    cliente_http.post("/test-drives", json={**TEST_DRIVE, "moto_id": MOTO_KAWASAKI})

    cola = cliente_http.get("/asesor/test-drives", headers=token_de(LAURA)).json()

    assert [t["codigo"] for t in cola] == [primero["codigo"], segundo["codigo"]]
    assert all(t["estado"] == "PENDIENTE" for t in cola)


def test_atender_el_siguiente_lo_programa_y_sale_de_la_cola(cliente_http, token_de):
    primero = cliente_http.post("/test-drives", json=TEST_DRIVE).json()
    segundo = cliente_http.post("/test-drives", json=TEST_DRIVE).json()

    respuesta = cliente_http.post(
        "/asesor/test-drives/siguiente",
        json={"fecha": "2026-11-15T10:00:00"},
        headers=token_de(LAURA),
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["codigo"] == primero["codigo"]
    assert cuerpo["estado"] == "PROGRAMADO"
    assert cuerpo["fecha_programada"] == "2026-11-15T10:00:00-05:00"
    cola = cliente_http.get("/asesor/test-drives", headers=token_de(LAURA)).json()
    assert [t["codigo"] for t in cola] == [segundo["codigo"]]


def test_atender_con_la_cola_vacia_responde_404(cliente_http, token_de):
    respuesta = cliente_http.post(
        "/asesor/test-drives/siguiente",
        json={"fecha": "2026-11-15T10:00:00"},
        headers=token_de(LAURA),
    )

    assert respuesta.status_code == 404


def test_programar_en_el_pasado_responde_422(cliente_http, token_de):
    cliente_http.post("/test-drives", json=TEST_DRIVE)

    respuesta = cliente_http.post(
        "/asesor/test-drives/siguiente",
        json={"fecha": "2026-11-01T10:00:00"},
        headers=token_de(LAURA),
    )

    assert respuesta.status_code == 422
