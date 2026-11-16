import sqlite3

import pytest
from sqlalchemy import create_engine

import app.infrastructure.models  # noqa: F401
from app.infrastructure.db.base import Base
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


def _cabeceras_admin(cliente_sqlite) -> dict:
    login = cliente_sqlite.post(
        "/auth/login", json={"correo": "admin@candela.com", "contrasena": CONTRASENA_ADMIN}
    )
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_buscar_por_cuota_guarda_la_busqueda_en_sqlite(cliente_sqlite, ruta_base_datos):
    respuesta = cliente_sqlite.get(
        "/motos/por-cuota",
        params={"cuota_maxima_cop": 900_000, "licencia": "A2", "uso": "TRABAJO"},
    )

    assert respuesta.status_code == 200, respuesta.text
    filas = _consultar(
        ruta_base_datos, "SELECT cuota_maxima_cop, categoria_licencia, uso FROM busquedas"
    )
    assert filas == [(900_000, "A2", "TRABAJO")]


def test_los_parametros_que_cambia_el_admin_quedan_en_sqlite(cliente_sqlite, ruta_base_datos):
    cabeceras = _cabeceras_admin(cliente_sqlite)
    actuales = cliente_sqlite.get("/parametros-costo", headers=cabeceras).json()
    actuales["precio_galon_cop"] = 17_500

    respuesta = cliente_sqlite.put("/parametros-costo", json=actuales, headers=cabeceras)

    assert respuesta.status_code == 200, respuesta.text
    assert _consultar(ruta_base_datos, "SELECT precio_galon_cop FROM parametros_costo") == [
        (17_500,)
    ]
    assert (
        cliente_sqlite.get("/parametros-costo", headers=cabeceras).json()["valor_matricula_cop"]
        == 520_000
    )


@pytest.fixture
def base_de_datos_vieja(ruta_base_datos):
    motor = create_engine(f"sqlite:///{ruta_base_datos.as_posix()}")
    Base.metadata.create_all(motor)
    motor.dispose()
    with sqlite3.connect(ruta_base_datos) as conexion:
        for tabla, columna in [
            ("parametros_costo", "valor_matricula_cop"),
            ("parametros_costo", "valor_tramites_cop"),
            ("parametros_costo", "tasa_mensual"),
            ("busquedas", "categoria_licencia"),
        ]:
            conexion.execute(f"ALTER TABLE {tabla} DROP COLUMN {columna}")
    return ruta_base_datos


def test_una_base_de_datos_vieja_se_actualiza_sola_al_arrancar(base_de_datos_vieja, cliente_sqlite):
    busqueda = cliente_sqlite.get("/motos/por-cuota", params={"cuota_maxima_cop": 600_000})
    costo = cliente_sqlite.get(f"/motos/{_primera_moto(cliente_sqlite)}/costo-real")

    assert busqueda.status_code == 200, busqueda.text
    assert costo.status_code == 200, costo.text
    assert _consultar(
        base_de_datos_vieja, "SELECT valor_matricula_cop, valor_tramites_cop FROM parametros_costo"
    ) == [(520_000, 380_000)]


def test_el_radar_de_demanda_lee_las_busquedas_guardadas_en_sqlite(cliente_sqlite):
    for cuota in (250_000, 1_200_000):
        cliente_sqlite.get("/motos/por-cuota", params={"cuota_maxima_cop": cuota})

    respuesta = cliente_sqlite.get("/reportes/demanda", headers=_cabeceras_admin(cliente_sqlite))

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["total_busquedas"] == 2
    assert {fila["rango"] for fila in cuerpo["filas"]} == {"Menos de $300.000", "$800.000 o más"}
    assert any(fila["motos_en_stock"] > 0 for fila in cuerpo["filas"])
