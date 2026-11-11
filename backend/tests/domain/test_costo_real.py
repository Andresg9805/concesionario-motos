import pytest

from app.domain.catalogo import UsoMoto
from app.domain.costo_real import CostoMensual, ParametrosCosto, PerfilUso, TarifaSoat
from app.domain.excepciones import EntidadNoEncontradaError


def parametros() -> ParametrosCosto:
    return ParametrosCosto(
        precio_galon_cop=16_000,
        porcentaje_impuesto=1.5,
        tarifas_soat=[
            TarifaSoat(cilindraje_min=0, cilindraje_max=99, valor_anual_cop=240_000),
            TarifaSoat(cilindraje_min=100, cilindraje_max=200, valor_anual_cop=480_000),
            TarifaSoat(cilindraje_min=201, cilindraje_max=2000, valor_anual_cop=600_000),
        ],
    )


def test_soat_mensual_segun_cilindraje():
    assert parametros().soat_mensual(150) == 40_000
    assert parametros().soat_mensual(399) == 50_000


def test_sin_tarifa_de_soat_falla():
    with pytest.raises(EntidadNoEncontradaError):
        parametros().soat_mensual(3_000)


def test_motos_de_hasta_125_cc_no_pagan_impuesto():
    assert parametros().impuesto_mensual(8_000_000, 125) == 0


def test_impuesto_mensual_para_motos_de_mas_de_125_cc():
    assert parametros().impuesto_mensual(24_000_000, 399) == 30_000


def test_tarifa_aplica_en_los_limites():
    tarifa = TarifaSoat(cilindraje_min=100, cilindraje_max=200, valor_anual_cop=480_000)
    assert tarifa.aplica(100)
    assert tarifa.aplica(200)
    assert not tarifa.aplica(201)


def test_costo_mensual_suma_todo():
    costo = CostoMensual(
        cuota_credito_cop=500_000,
        gasolina_cop=80_000,
        soat_cop=40_000,
        mantenimiento_cop=30_000,
        impuesto_cop=10_000,
    )
    assert costo.total() == 660_000


def test_ganancia_mensual_del_modo_trabajo():
    perfil = PerfilUso(
        km_mes=2_000, uso=UsoMoto.TRABAJO, ganancia_diaria_cop=80_000, dias_trabajo_mes=26
    )
    assert perfil.ganancia_mensual() == 2_080_000


def test_perfil_sin_trabajo_no_tiene_ganancia():
    assert PerfilUso(km_mes=500, uso=UsoMoto.CIUDAD).ganancia_mensual() == 0


def test_kilometros_negativos_no_son_validos():
    with pytest.raises(ValueError):
        PerfilUso(km_mes=-1, uso=UsoMoto.CIUDAD)


def test_porcentaje_de_impuesto_fuera_de_rango():
    with pytest.raises(ValueError):
        ParametrosCosto(precio_galon_cop=16_000, porcentaje_impuesto=150)
