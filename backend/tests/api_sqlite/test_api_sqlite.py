import sqlite3

from tests.api_sqlite.conftest import CONTRASENA_ADMIN

CLIENTE = {
    "nombre": "Ana Pérez",
    "correo": "ana.sqlite@correo.com",
    "celular": "3001234567",
    "contrasena": "clave-segura-123",
}


def _primera_moto(cliente_sqlite) -> int:
    respuesta = cliente_sqlite.get("/motos")
    assert respuesta.status_code == 200
    return respuesta.json()[0]["id"]


def _cotizar(cliente_sqlite, moto_id: int) -> dict:
    respuesta = cliente_sqlite.post(
        "/cotizaciones",
        json={
            "moto_id": moto_id,
            "nombre": CLIENTE["nombre"],
            "correo": CLIENTE["correo"],
            "celular": CLIENTE["celular"],
            "acepta_contacto": True,
            "cuota_inicial_cop": 1_000_000,
            "plazo_meses": 36,
        },
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _consultar(ruta_base_datos, sql: str, *parametros) -> list[tuple]:
    with sqlite3.connect(ruta_base_datos) as conexion:
        return conexion.execute(sql, parametros).fetchall()


def test_registrar_y_cotizar_guarda_la_cotizacion_en_sqlite(cliente_sqlite, ruta_base_datos):
    registro = cliente_sqlite.post("/auth/registro", json=CLIENTE)
    assert registro.status_code == 201, registro.text
    moto_id = _primera_moto(cliente_sqlite)

    cotizacion = _cotizar(cliente_sqlite, moto_id)

    assert cotizacion["codigo"].startswith("CM-")
    filas = _consultar(
        ruta_base_datos,
        "SELECT moto_id FROM cotizaciones WHERE codigo_seguimiento = ?",
        cotizacion["codigo"],
    )
    assert filas == [(moto_id,)]
    usuarios = _consultar(
        ruta_base_datos,
        "SELECT COUNT(*) FROM personas WHERE correo = ?",
        CLIENTE["correo"],
    )
    assert usuarios == [(1,)]


def test_borrar_una_moto_con_cotizacion_responde_409(cliente_sqlite, ruta_base_datos):
    moto_id = _primera_moto(cliente_sqlite)
    _cotizar(cliente_sqlite, moto_id)
    login = cliente_sqlite.post(
        "/auth/login", json={"correo": "admin@candela.com", "contrasena": CONTRASENA_ADMIN}
    )
    assert login.status_code == 200, login.text
    cabeceras = {"Authorization": f"Bearer {login.json()['access_token']}"}

    respuesta = cliente_sqlite.delete(f"/admin/motos/{moto_id}", headers=cabeceras)

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": "No se puede borrar porque ya tiene cotizaciones o pedidos"
    }
    assert _consultar(ruta_base_datos, "SELECT COUNT(*) FROM motos WHERE id = ?", moto_id) == [(1,)]
