from datetime import datetime, timedelta

import pytest

from app.domain.catalogo import Busqueda, CategoriaLicencia, UsoMoto
from app.infrastructure.db.repositorios.busqueda import RepositorioBusquedasSQLAlchemy
from app.infrastructure.db.repositorios.conversiones import ZONA_COLOMBIA
from app.infrastructure.db.seeds.marcas import seed_marcas

AHORA = datetime(2026, 11, 16, 10, 30, tzinfo=ZONA_COLOMBIA)


@pytest.fixture
def busquedas(sesion):
    seed_marcas(sesion)
    sesion.flush()
    return RepositorioBusquedasSQLAlchemy(sesion)


def busqueda(cuota: int, minutos: int = 0, marca_id: int | None = 1, resultados: int = 3):
    return Busqueda(
        fecha=AHORA + timedelta(minutes=minutos),
        cuota_maxima_cop=cuota,
        cuota_inicial_cop=1_000_000,
        categoria_licencia=CategoriaLicencia.A2,
        uso=UsoMoto.TRABAJO,
        marca_id=marca_id,
        cantidad_resultados=resultados,
    )


def test_guardar_le_pone_id_y_conserva_los_datos(busquedas):
    guardada = busquedas.guardar(busqueda(450_000))

    assert guardada.id is not None
    assert guardada.cuota_maxima_cop == 450_000
    assert guardada.categoria_licencia == CategoriaLicencia.A2
    assert guardada.uso == UsoMoto.TRABAJO
    assert guardada.fecha == AHORA


def test_listar_devuelve_la_mas_reciente_primero(busquedas):
    busquedas.guardar(busqueda(300_000, minutos=0))
    busquedas.guardar(busqueda(800_000, minutos=5))

    assert [b.cuota_maxima_cop for b in busquedas.listar()] == [800_000, 300_000]


def test_una_busqueda_sin_marca_y_sin_resultados_tambien_se_guarda(busquedas):
    busquedas.guardar(busqueda(200_000, marca_id=None, resultados=0))

    [guardada] = busquedas.listar()
    assert guardada.marca_id is None
    assert guardada.cantidad_resultados == 0
