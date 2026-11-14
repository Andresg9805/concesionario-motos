from datetime import date

import pytest

from app.domain.catalogo import (
    CategoriaLicencia,
    Marca,
    Moto,
    PlanCredito,
    TasaCambio,
    TipoMoto,
)
from app.domain.excepciones import CreditoInvalidoError
from tests.domain import fabricas


def test_marca_fuera_de_las_tres_japonesas_no_se_permite():
    with pytest.raises(ValueError):
        Marca(nombre="Bajaj", color_hex="#000000")


@pytest.mark.parametrize(
    ("cilindraje", "categoria"),
    [(110, CategoriaLicencia.A1), (125, CategoriaLicencia.A1), (126, CategoriaLicencia.A2)],
)
def test_categoria_por_cilindraje(cilindraje, categoria):
    assert Moto.categoria_por_cilindraje(cilindraje) == categoria


def test_la_moto_calcula_su_categoria_si_no_se_la_dan():
    assert fabricas.moto(cilindraje_cc=399).categoria_licencia == CategoriaLicencia.A2


def test_categoria_que_no_cuadra_con_el_cilindraje_falla():
    with pytest.raises(ValueError):
        Moto(
            marca=fabricas.marca(),
            modelo="Ninja 400",
            anio=2026,
            cilindraje_cc=399,
            tipo="DEPORTIVA",
            categoria_licencia=CategoriaLicencia.A1,
            precio_cop=30_000_000,
            consumo_km_galon=90,
            costo_mantenimiento_km_cop=60,
        )


def test_licencia_a1_solo_sirve_para_motos_a1():
    assert fabricas.moto(cilindraje_cc=110).apta_para(CategoriaLicencia.A1)
    assert not fabricas.moto(cilindraje_cc=399).apta_para(CategoriaLicencia.A1)


def test_licencia_a2_sirve_para_cualquier_moto():
    assert fabricas.moto(cilindraje_cc=110).apta_para(CategoriaLicencia.A2)
    assert fabricas.moto(cilindraje_cc=399).apta_para(CategoriaLicencia.A2)


def test_disponible_solo_si_hay_stock():
    assert fabricas.moto(stock=1).esta_disponible()
    assert not fabricas.moto(stock=0).esta_disponible()


def test_precio_en_dolares_con_la_trm():
    trm = TasaCambio(valor=4_000, fecha=date(2026, 11, 9))
    assert fabricas.moto(precio_cop=30_000_000).precio_en_usd(trm) == 7_500.0


def test_trm_en_cero_no_es_valida():
    with pytest.raises(ValueError):
        TasaCambio(valor=0, fecha=date(2026, 11, 9))


def test_cuota_mensual_con_formula_de_cuota_fija():
    plan = fabricas.plan()
    assert plan.monto_financiado() == 25_000_000
    assert plan.cuota_mensual() == 980_821


def test_cuota_sin_intereses_divide_el_monto():
    plan = PlanCredito(precio_cop=12_000_000, cuota_inicial_cop=0, plazo_meses=12, tasa_mensual=0)
    assert plan.cuota_mensual() == 1_000_000


def test_precio_maximo_es_la_formula_al_reves():
    cuota = fabricas.plan().cuota_mensual()
    precio = PlanCredito.precio_maximo_para_cuota(cuota, 5_000_000, 36, 0.02)
    assert precio == pytest.approx(30_000_000, abs=50)


def test_precio_maximo_sin_intereses():
    assert PlanCredito.precio_maximo_para_cuota(500_000, 1_000_000, 10, 0) == 6_000_000


@pytest.mark.parametrize(
    ("precio", "inicial", "plazo", "tasa"),
    [(10_000_000, 11_000_000, 12, 0.02), (10_000_000, 0, 0, 0.02), (10_000_000, 0, 12, -0.01)],
)
def test_planes_invalidos(precio, inicial, plazo, tasa):
    with pytest.raises(CreditoInvalidoError):
        PlanCredito(
            precio_cop=precio, cuota_inicial_cop=inicial, plazo_meses=plazo, tasa_mensual=tasa
        )


def test_cuota_cero_no_permite_buscar():
    with pytest.raises(CreditoInvalidoError):
        PlanCredito.precio_maximo_para_cuota(0, 0, 24, 0.02)


def test_los_tipos_de_moto_son_naked_doble_proposito_deportiva_y_trail():
    assert {tipo.value for tipo in TipoMoto} == {"NAKED", "DOBLE_PROPOSITO", "DEPORTIVA", "TRAIL"}


def test_ya_no_existen_calle_ni_scooter():
    assert "CALLE" not in TipoMoto.__members__
    assert "SCOOTER" not in TipoMoto.__members__


@pytest.mark.parametrize("tipo", ["NAKED", "TRAIL"])
def test_se_puede_crear_una_moto_naked_o_trail(tipo):
    moto = fabricas.moto(tipo=TipoMoto(tipo))
    assert moto.tipo == TipoMoto(tipo)
