import pytest

from app.domain.atencion import Rol, Usuario
from tests.atencion.conftest import COTIZACION, MOTO_KAWASAKI


@pytest.fixture
def ana(usuarios):
    return usuarios.guardar(
        Usuario(
            nombre="Ana Pérez",
            correo="ana@correo.com",
            telefono="3001234567",
            hash_contrasena="hash",
            rol=Rol.CLIENTE,
        )
    )


def test_el_cliente_ve_las_cotizaciones_que_hizo_con_su_correo(cliente_http, ana, token_de):
    primera = cliente_http.post("/cotizaciones", json=COTIZACION).json()
    segunda = cliente_http.post(
        "/cotizaciones", json={**COTIZACION, "moto_id": MOTO_KAWASAKI}
    ).json()

    respuesta = cliente_http.get("/mis-cotizaciones", headers=token_de("ana@correo.com"))

    assert respuesta.status_code == 200
    codigos = {cotizacion["codigo"] for cotizacion in respuesta.json()}
    assert codigos == {primera["codigo"], segunda["codigo"]}
    assert all(c["cuota_mensual_cop"] > 0 for c in respuesta.json())


def test_no_ve_las_cotizaciones_de_otra_persona(cliente_http, ana, token_de):
    cliente_http.post(
        "/cotizaciones", json={**COTIZACION, "correo": "otra@correo.com", "nombre": "Otra Persona"}
    )

    respuesta = cliente_http.get("/mis-cotizaciones", headers=token_de("ana@correo.com"))

    assert respuesta.json() == []


def test_sin_sesion_responde_401(cliente_http):
    assert cliente_http.get("/mis-cotizaciones").status_code == 401


def test_un_asesor_no_puede_usarlo(cliente_http, token_de):
    respuesta = cliente_http.get("/mis-cotizaciones", headers=token_de("laura.ruiz@candela.com"))
    assert respuesta.status_code == 403
