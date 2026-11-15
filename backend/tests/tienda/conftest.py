import os

os.environ.setdefault("JWT_SECRET", "secreto-de-pruebas-con-mas-de-32-caracteres")

import pytest
from fastapi.testclient import TestClient

from app.api import dependencias
from app.domain.atencion import Rol, Usuario
from app.infrastructure.memoria.datos_prueba import asesores_iniciales
from app.infrastructure.memoria.tienda import (
    RepositorioAccesoriosEnMemoria,
    RepositorioDireccionesEnMemoria,
    RepositorioUbicacionesEnMemoria,
)
from app.infrastructure.memoria.usuarios import RepositorioUsuariosEnMemoria
from app.infrastructure.seguridad.jwt_emisor import EmisorTokensJWT
from app.main import app
from tests.datos_accesorios import accesorios_de_prueba

DIRECCION = {
    "nombre_recibe": "Ana Pérez",
    "telefono": "3001234567",
    "departamento_codigo": "11",
    "municipio_codigo": "11001",
    "municipio_nombre": "Bogotá D.C.",
    "direccion": "Calle 26 # 13-19",
    "detalle": "Apto 302",
}


@pytest.fixture
def usuarios():
    repositorio = RepositorioUsuariosEnMemoria()
    for asesor in asesores_iniciales("hash"):
        repositorio.guardar(asesor)
    for nombre, correo in (("Ana Pérez", "ana@correo.com"), ("Luis Gómez", "luis@correo.com")):
        repositorio.guardar(
            Usuario(
                nombre=nombre,
                correo=correo,
                telefono="3001234567",
                hash_contrasena="hash",
                rol=Rol.CLIENTE,
            )
        )
    return repositorio


@pytest.fixture
def emisor():
    return EmisorTokensJWT(os.environ["JWT_SECRET"], 60)


@pytest.fixture
def cliente_http(usuarios, emisor):
    accesorios = RepositorioAccesoriosEnMemoria(accesorios_de_prueba())
    ubicaciones = RepositorioUbicacionesEnMemoria()
    direcciones = RepositorioDireccionesEnMemoria()
    app.dependency_overrides[dependencias.obtener_repositorio_accesorios] = lambda: accesorios
    app.dependency_overrides[dependencias.obtener_repositorio_ubicaciones] = lambda: ubicaciones
    app.dependency_overrides[dependencias.obtener_repositorio_direcciones] = lambda: direcciones
    app.dependency_overrides[dependencias.obtener_repositorio_usuarios] = lambda: usuarios
    app.dependency_overrides[dependencias.obtener_emisor_tokens] = lambda: emisor
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def token_de(usuarios, emisor):
    def token(correo):
        return {"Authorization": f"Bearer {emisor.emitir(usuarios.buscar_por_correo(correo))}"}

    return token
