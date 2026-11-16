import pytest

from app.domain.costo_real import ParametrosCosto, TarifaSoat
from app.infrastructure.db.repositorios.parametros import RepositorioParametrosSQLAlchemy
from app.infrastructure.db.seeds.parametros_costo import seed_parametros_costo


@pytest.fixture
def parametros(sesion):
    seed_parametros_costo(sesion)
    sesion.flush()
    return RepositorioParametrosSQLAlchemy(sesion)


def test_obtener_trae_los_parametros_iniciales(parametros):
    actuales = parametros.obtener()

    assert actuales.precio_galon_cop == 16_200
    assert actuales.porcentaje_impuesto == 1.5
    assert actuales.valor_matricula_cop == 520_000
    assert actuales.valor_tramites_cop == 380_000
    assert actuales.tasa_mensual == pytest.approx(0.0179)
    assert [t.valor_anual_cop for t in actuales.tarifas_soat] == [256_000, 343_000, 790_000]


def test_guardar_cambia_los_valores_y_las_tarifas(parametros):
    nuevos = ParametrosCosto(
        precio_galon_cop=17_000,
        porcentaje_impuesto=2.0,
        tarifas_soat=[
            TarifaSoat(cilindraje_min=0, cilindraje_max=200, valor_anual_cop=300_000),
            TarifaSoat(cilindraje_min=201, cilindraje_max=100_000, valor_anual_cop=800_000),
        ],
        valor_matricula_cop=600_000,
        valor_tramites_cop=400_000,
        tasa_mensual=0.02,
    )

    guardados = parametros.guardar(nuevos)

    assert guardados.precio_galon_cop == 17_000
    assert guardados.porcentaje_impuesto == 2.0
    assert guardados.valor_matricula_cop == 600_000
    assert guardados.tasa_mensual == pytest.approx(0.02)
    assert len(parametros.obtener().tarifas_soat) == 2
    assert parametros.obtener().soat_anual(150) == 300_000


def test_sin_parametros_en_la_base_de_datos_lanza_error(sesion):
    with pytest.raises(LookupError):
        RepositorioParametrosSQLAlchemy(sesion).obtener()
