from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api import dependencias
from app.application.motos import BuscarMotosPorCuota
from app.infrastructure.memoria.catalogo import (
    RepositorioBusquedasEnMemoria,
    RepositorioMarcasEnMemoria,
    RepositorioMotosEnMemoria,
    RepositorioParametrosEnMemoria,
    RepositorioSimulacionesEnMemoria,
)
from app.main import app

AHORA = datetime(2026, 11, 12, 9, 30, tzinfo=UTC)


@pytest.fixture
def marcas():
    return RepositorioMarcasEnMemoria()


@pytest.fixture
def motos():
    return RepositorioMotosEnMemoria()


@pytest.fixture
def parametros():
    return RepositorioParametrosEnMemoria()


@pytest.fixture
def busquedas():
    return RepositorioBusquedasEnMemoria()


@pytest.fixture
def simulaciones():
    return RepositorioSimulacionesEnMemoria()


@pytest.fixture
def buscar_por_cuota(motos, parametros, busquedas, simulaciones):
    return BuscarMotosPorCuota(motos, parametros, busquedas, simulaciones, reloj=lambda: AHORA)


@pytest.fixture
def cliente_http(marcas, motos, parametros, busquedas, simulaciones):
    app.dependency_overrides[dependencias.obtener_repositorio_marcas] = lambda: marcas
    app.dependency_overrides[dependencias.obtener_repositorio_motos] = lambda: motos
    app.dependency_overrides[dependencias.obtener_repositorio_parametros] = lambda: parametros
    app.dependency_overrides[dependencias.obtener_repositorio_busquedas] = lambda: busquedas
    app.dependency_overrides[dependencias.obtener_repositorio_simulaciones] = lambda: simulaciones
    yield TestClient(app)
    app.dependency_overrides.clear()
