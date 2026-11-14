from typing import Annotated

import jwt
from fastapi import Depends

from app.api.dependencias import requerir_rol
from app.domain.seguridad import DatosToken
from app.main import app
from tests.auth.conftest import SECRETO

REGISTRO = {
    "nombre": "Ana Pérez",
    "correo": "ana@correo.com",
    "celular": "3001234567",
    "contrasena": "clave1234",
}


@app.get("/pruebas/solo-asesor", include_in_schema=False)
def ruta_solo_asesor(sesion: Annotated[DatosToken, Depends(requerir_rol("ASESOR", "ADMIN"))]):
    return {"id": sesion.usuario_id}


def iniciar_sesion(cliente_http, correo, contrasena):
    return cliente_http.post("/auth/login", json={"correo": correo, "contrasena": contrasena})


def test_registro_crea_cliente_sin_exponer_hash(cliente_http, usuarios, clientes):
    respuesta = cliente_http.post("/auth/registro", json=REGISTRO)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo == {
        "id": 1,
        "nombre": "Ana Pérez",
        "correo": "ana@correo.com",
        "celular": "3001234567",
        "rol": "CLIENTE",
        "marca": None,
    }
    assert "hash_contrasena" not in respuesta.text
    assert "clave1234" not in respuesta.text
    assert usuarios.buscar_por_correo("ana@correo.com").hash_contrasena.startswith("$2")
    assert clientes.buscar_por_correo("ana@correo.com").usuario.id == 1


def test_registro_rechaza_rol_en_el_cuerpo(cliente_http):
    respuesta = cliente_http.post("/auth/registro", json={**REGISTRO, "rol": "ADMIN"})

    assert respuesta.status_code == 422


def test_registro_con_correo_repetido_responde_409(cliente_http):
    cliente_http.post("/auth/registro", json=REGISTRO)

    respuesta = cliente_http.post(
        "/auth/registro", json={**REGISTRO, "correo": "  ANA@correo.com "}
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "Ya existe una cuenta con ese correo"}


def test_registro_valida_celular_y_contrasena(cliente_http):
    assert (
        cliente_http.post("/auth/registro", json={**REGISTRO, "celular": "12345"}).status_code
        == 422
    )
    assert (
        cliente_http.post("/auth/registro", json={**REGISTRO, "contrasena": "corta"}).status_code
        == 422
    )
    assert (
        cliente_http.post("/auth/registro", json={**REGISTRO, "contrasena": "ñ" * 40}).status_code
        == 422
    )


def test_login_devuelve_token_bearer_con_payload_de_cliente(cliente_http):
    cliente_http.post("/auth/registro", json=REGISTRO)

    respuesta = iniciar_sesion(cliente_http, "ana@correo.com", "clave1234")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "bearer"
    payload = jwt.decode(cuerpo["access_token"], SECRETO, algorithms=["HS256"])
    assert set(payload) == {"sub", "nombre", "rol", "marca", "exp"}
    assert payload["sub"] == "1"
    assert payload["nombre"] == "Ana Pérez"
    assert payload["rol"] == "CLIENTE"
    assert payload["marca"] is None


def test_login_de_asesora_incluye_marca(cliente_http, asesora_yamaha):
    respuesta = iniciar_sesion(cliente_http, "daniela@candela.com", "asesora1234")

    payload = jwt.decode(respuesta.json()["access_token"], SECRETO, algorithms=["HS256"])
    assert payload["sub"] == str(asesora_yamaha.id)
    assert payload["rol"] == "ASESOR"
    assert payload["marca"] == "yamaha"


def test_login_con_contrasena_incorrecta_responde_401(cliente_http):
    cliente_http.post("/auth/registro", json=REGISTRO)

    respuesta = iniciar_sesion(cliente_http, "ana@correo.com", "otra-clave")

    assert respuesta.status_code == 401
    assert respuesta.json() == {"detail": "Correo o contraseña incorrectos"}


def test_login_con_correo_inexistente_responde_401(cliente_http):
    respuesta = iniciar_sesion(cliente_http, "nadie@correo.com", "clave1234")

    assert respuesta.status_code == 401
    assert respuesta.json() == {"detail": "Correo o contraseña incorrectos"}


def test_yo_requiere_token_valido(cliente_http, asesora_yamaha):
    assert cliente_http.get("/auth/yo").status_code == 401
    assert (
        cliente_http.get("/auth/yo", headers={"Authorization": "Bearer basura"}).status_code == 401
    )

    token = iniciar_sesion(cliente_http, "daniela@candela.com", "asesora1234").json()
    respuesta = cliente_http.get(
        "/auth/yo", headers={"Authorization": f"Bearer {token['access_token']}"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": asesora_yamaha.id,
        "nombre": "Daniela Pardo",
        "rol": "ASESOR",
        "marca": "yamaha",
    }


def test_requerir_rol_bloquea_a_un_cliente(cliente_http, asesora_yamaha):
    cliente_http.post("/auth/registro", json=REGISTRO)
    token_cliente = iniciar_sesion(cliente_http, "ana@correo.com", "clave1234").json()
    token_asesora = iniciar_sesion(cliente_http, "daniela@candela.com", "asesora1234").json()

    prohibido = cliente_http.get(
        "/pruebas/solo-asesor",
        headers={"Authorization": f"Bearer {token_cliente['access_token']}"},
    )
    permitido = cliente_http.get(
        "/pruebas/solo-asesor",
        headers={"Authorization": f"Bearer {token_asesora['access_token']}"},
    )

    assert prohibido.status_code == 403
    assert permitido.status_code == 200


def test_cors_permite_localhost_4200(cliente_http):
    respuesta = cliente_http.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == "http://localhost:4200"


def test_cors_rechaza_otros_origenes(cliente_http):
    respuesta = cliente_http.options(
        "/auth/login",
        headers={"Origin": "http://evil.com", "Access-Control-Request-Method": "POST"},
    )

    assert "access-control-allow-origin" not in respuesta.headers
