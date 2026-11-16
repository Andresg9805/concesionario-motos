import pytest

from app.api import dependencias
from app.domain.atencion import Rol


@pytest.fixture(autouse=True)
def sin_cache():
    dependencias.obtener_repositorio_usuarios.cache_clear()
    yield
    dependencias.obtener_repositorio_usuarios.cache_clear()


def test_el_administrador_demo_usa_la_contrasena_del_entorno(monkeypatch):
    monkeypatch.setenv("CONTRASENA_ADMIN_DEMO", "clave-admin-demo")
    admin = dependencias.obtener_repositorio_usuarios().buscar_por_correo("admin@candela.com")
    assert admin is not None
    assert admin.rol == Rol.ADMIN
    assert dependencias.obtener_hasheador().verificar("clave-admin-demo", admin.hash_contrasena)


def test_sin_variable_el_administrador_demo_tiene_una_contrasena_aleatoria(monkeypatch):
    monkeypatch.delenv("CONTRASENA_ADMIN_DEMO", raising=False)
    admin = dependencias.obtener_repositorio_usuarios().buscar_por_correo("admin@candela.com")
    assert admin is not None
    assert not dependencias.obtener_hasheador().verificar("", admin.hash_contrasena)
