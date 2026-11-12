import os

os.environ.setdefault("JWT_SECRET", "secreto-de-pruebas-con-mas-de-32-caracteres")

import pytest
from fastapi.testclient import TestClient

from app.api import dependencias
from app.domain.atencion import Rol, Usuario
from app.domain.catalogo import Marca
from app.infrastructure.memoria.usuarios import (
    RepositorioClientesEnMemoria,
    RepositorioUsuariosEnMemoria,
)
from app.infrastructure.seguridad.bcrypt_hasheador import HasheadorBcrypt
from app.infrastructure.seguridad.jwt_emisor import EmisorTokensJWT
from app.main import app

SECRETO = os.environ["JWT_SECRET"]


@pytest.fixture
def hasheador():
    return HasheadorBcrypt(rondas=4)


@pytest.fixture
def emisor():
    return EmisorTokensJWT(SECRETO, 60)


@pytest.fixture
def usuarios():
    return RepositorioUsuariosEnMemoria()


@pytest.fixture
def clientes():
    return RepositorioClientesEnMemoria()


@pytest.fixture
def cliente_http(usuarios, clientes, hasheador, emisor):
    app.dependency_overrides[dependencias.obtener_repositorio_usuarios] = lambda: usuarios
    app.dependency_overrides[dependencias.obtener_repositorio_clientes] = lambda: clientes
    app.dependency_overrides[dependencias.obtener_hasheador] = lambda: hasheador
    app.dependency_overrides[dependencias.obtener_emisor_tokens] = lambda: emisor
    app.dependency_overrides[dependencias.obtener_hash_senuelo] = lambda: hasheador.hashear("x")
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def asesora_yamaha(usuarios, hasheador):
    return usuarios.guardar(
        Usuario(
            nombre="Daniela Pardo",
            correo="daniela@candela.com",
            telefono="3109876543",
            hash_contrasena=hasheador.hashear("asesora1234"),
            rol=Rol.ASESOR,
            marca_especialidad=Marca(id=3, nombre="Yamaha", color_hex="#0033A0"),
        )
    )
