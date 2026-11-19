from datetime import timedelta

import pytest

from app.domain.catalogo import CategoriaLicencia, Moto, PlanCredito
from app.domain.excepciones import CreditoInvalidoError
from tests.domain import fabricas


@pytest.mark.parametrize(
    ("cilindraje", "categoria"),
    [(124, CategoriaLicencia.A1), (125, CategoriaLicencia.A1), (126, CategoriaLicencia.A2)],
)
def test_frontera_de_la_licencia_en_125_cc(cilindraje, categoria):
    assert Moto.categoria_por_cilindraje(cilindraje) == categoria


@pytest.mark.parametrize(
    ("despues", "vencida"),
    [
        (timedelta(minutes=14, seconds=59), False),
        (timedelta(minutes=15), False),
        (timedelta(minutes=15, seconds=1), True),
    ],
)
def test_frontera_de_la_reserva_de_15_minutos(despues, vencida):
    pedido = fabricas.pedido()
    assert pedido.reserva_vencida(fabricas.AHORA + despues) is vencida


@pytest.mark.parametrize("plazo", [1, 2])
def test_plazo_valido_desde_un_mes(plazo):
    plan = PlanCredito(
        precio_cop=10_000_000, cuota_inicial_cop=0, plazo_meses=plazo, tasa_mensual=0.0179
    )
    assert plan.cuota_mensual() > 0


@pytest.mark.parametrize("plazo", [-1, 0])
def test_plazo_menor_a_un_mes_es_invalido(plazo):
    with pytest.raises(CreditoInvalidoError):
        PlanCredito(
            precio_cop=10_000_000, cuota_inicial_cop=0, plazo_meses=plazo, tasa_mensual=0.0179
        )


@pytest.mark.parametrize(("inicial", "valido"), [(-1, False), (0, True), (1, True)])
def test_frontera_de_la_cuota_inicial_en_cero(inicial, valido):
    if valido:
        plan = PlanCredito(
            precio_cop=10_000_000, cuota_inicial_cop=inicial, plazo_meses=12, tasa_mensual=0.0179
        )
        assert plan.monto_financiado() == 10_000_000 - inicial
    else:
        with pytest.raises(CreditoInvalidoError):
            PlanCredito(
                precio_cop=10_000_000,
                cuota_inicial_cop=inicial,
                plazo_meses=12,
                tasa_mensual=0.0179,
            )
