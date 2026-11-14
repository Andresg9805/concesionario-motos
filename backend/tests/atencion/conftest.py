import os

os.environ.setdefault("JWT_SECRET", "secreto-de-pruebas-con-mas-de-32-caracteres")

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.api import dependencias
from app.application.atencion import ZONA_COLOMBIA
from app.domain.atencion import Rol, Usuario
from app.infrastructure.memoria.atencion import (
    RepositorioCotizacionesEnMemoria,
    RepositorioTestDrivesEnMemoria,
)
from app.infrastructure.memoria.catalogo import (
    RepositorioMotosEnMemoria,
    RepositorioParametrosEnMemoria,
)
from app.infrastructure.memoria.datos_prueba import asesores_iniciales, marcas_iniciales
from app.infrastructure.memoria.usuarios import (
    RepositorioClientesEnMemoria,
    RepositorioUsuariosEnMemoria,
)
from app.infrastructure.seguridad.jwt_emisor import EmisorTokensJWT
from app.main import app

AHORA = datetime(2026, 11, 13, 20, 0, tzinfo=ZONA_COLOMBIA)
MOTO_HONDA = 3
MOTO_KAWASAKI = 9

CONTACTO = {
    "nombre": "Ana Pérez",
    "correo": "ana@correo.com",
    "celular": "3001234567",
    "acepta_contacto": True,
}
COTIZACION = {**CONTACTO, "moto_id": MOTO_HONDA, "cuota_inicial_cop": 1_289_000, "plazo_meses": 36}
TEST_DRIVE = {**CONTACTO, "moto_id": MOTO_HONDA}


@pytest.fixture
def usuarios():
    repositorio = RepositorioUsuariosEnMemoria()
    for asesor in asesores_iniciales("hash"):
        repositorio.guardar(asesor)
    return repositorio


@pytest.fixture
def clientes():
    return RepositorioClientesEnMemoria()


@pytest.fixture
def cotizaciones():
    return RepositorioCotizacionesEnMemoria()


@pytest.fixture
def test_drives():
    return RepositorioTestDrivesEnMemoria()


@pytest.fixture
def emisor():
    return EmisorTokensJWT(os.environ["JWT_SECRET"], 60)


@pytest.fixture
def cliente_http(usuarios, clientes, cotizaciones, test_drives, emisor):
    app.dependency_overrides[dependencias.obtener_reloj_atencion] = lambda: lambda: AHORA
    motos = RepositorioMotosEnMemoria()
    parametros = RepositorioParametrosEnMemoria()
    app.dependency_overrides[dependencias.obtener_repositorio_motos] = lambda: motos
    app.dependency_overrides[dependencias.obtener_repositorio_parametros] = lambda: parametros
    app.dependency_overrides[dependencias.obtener_repositorio_usuarios] = lambda: usuarios
    app.dependency_overrides[dependencias.obtener_repositorio_clientes] = lambda: clientes
    app.dependency_overrides[dependencias.obtener_repositorio_cotizaciones] = lambda: cotizaciones
    app.dependency_overrides[dependencias.obtener_repositorio_test_drives] = lambda: test_drives
    app.dependency_overrides[dependencias.obtener_emisor_tokens] = lambda: emisor
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def token_de(usuarios, emisor):
    def token(correo):
        return {"Authorization": f"Bearer {emisor.emitir(usuarios.buscar_por_correo(correo))}"}

    return token


@pytest.fixture
def segunda_asesora_honda(usuarios):
    return usuarios.guardar(
        Usuario(
            nombre="Sofía Gómez",
            correo="sofia.gomez@candela.com",
            telefono="3004445566",
            hash_contrasena="hash",
            rol=Rol.ASESOR,
            marca_especialidad=marcas_iniciales()[0],
        )
    )
