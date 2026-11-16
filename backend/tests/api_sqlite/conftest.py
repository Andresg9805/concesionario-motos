import importlib
import sys

import pytest
from fastapi.testclient import TestClient

CONTRASENA_ADMIN = "contrasena-admin-sqlite"
CONTRASENA_ASESORES = "contrasena-asesores-sqlite"


def _modulos_app() -> list[str]:
    return [nombre for nombre in sys.modules if nombre == "app" or nombre.startswith("app.")]


@pytest.fixture
def ruta_base_datos(tmp_path):
    return tmp_path / "concesionario.db"


@pytest.fixture
def cliente_sqlite(ruta_base_datos, monkeypatch):
    monkeypatch.setenv("ALMACENAMIENTO", "sqlite")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{ruta_base_datos.as_posix()}")
    monkeypatch.setenv("JWT_SECRET", "secreto-de-pruebas-sqlite-con-mas-de-32-caracteres")
    monkeypatch.setenv("CONTRASENA_ADMIN_DEMO", CONTRASENA_ADMIN)
    monkeypatch.setenv("CONTRASENA_ASESORES_DEMO", CONTRASENA_ASESORES)
    originales = {nombre: sys.modules.pop(nombre) for nombre in _modulos_app()}
    try:
        principal = importlib.import_module("app.main")
        with TestClient(principal.app) as cliente:
            yield cliente
        importlib.import_module("app.infrastructure.db.conexion").engine.dispose()
    finally:
        for nombre in _modulos_app():
            del sys.modules[nombre]
        sys.modules.update(originales)
