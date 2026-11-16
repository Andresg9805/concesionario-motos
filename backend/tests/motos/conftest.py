from datetime import UTC, date, datetime

import pytest
from fastapi.testclient import TestClient

from app.api import dependencias
from app.application.motos import BuscarMotosPorCuota
from app.domain.catalogo import TasaCambio
from app.domain.puertos import ProveedorTasaCambio
from app.infrastructure.memoria.catalogo import (
    RepositorioBusquedasEnMemoria,
    RepositorioMarcasEnMemoria,
    RepositorioMotosEnMemoria,
    RepositorioParametrosEnMemoria,
    RepositorioSimulacionesEnMemoria,
)
from app.main import app

AHORA = datetime(2026, 11, 12, 9, 30, tzinfo=UTC)


class ProveedorTrmFalso(ProveedorTasaCambio):
    def __init__(self):
        self.trm = TasaCambio(valor=4_000.0, fecha=date(2026, 11, 16))
        self.llamadas = 0

    async def obtener_trm(self):
        self.llamadas += 1
        return self.trm


@pytest.fixture
def proveedor_trm():
    return ProveedorTrmFalso()


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
def cliente_http(marcas, motos, parametros, busquedas, simulaciones, proveedor_trm):
    app.dependency_overrides[dependencias.obtener_repositorio_marcas] = lambda: marcas
    app.dependency_overrides[dependencias.obtener_repositorio_motos] = lambda: motos
    app.dependency_overrides[dependencias.obtener_repositorio_parametros] = lambda: parametros
    app.dependency_overrides[dependencias.obtener_repositorio_busquedas] = lambda: busquedas
    app.dependency_overrides[dependencias.obtener_repositorio_simulaciones] = lambda: simulaciones
    app.dependency_overrides[dependencias.obtener_proveedor_trm] = lambda: proveedor_trm
    yield TestClient(app)
    app.dependency_overrides.clear()
