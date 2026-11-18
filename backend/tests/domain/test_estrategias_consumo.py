from app.domain.catalogo import UsoMoto
from app.domain.costo_real import PerfilUso
from app.domain.estrategias_consumo import (
    ESTRATEGIAS_CONSUMO,
    ConsumoCarretera,
    ConsumoCiudad,
    ConsumoTrabajo,
    EstrategiaConsumo,
)
from app.domain.servicios import CalculadoraCostoReal
from tests.domain.fabricas import moto, plan
from tests.domain.test_costo_real import parametros


def test_hay_una_estrategia_por_cada_uso():
    assert set(ESTRATEGIAS_CONSUMO) == set(UsoMoto)
    assert isinstance(ESTRATEGIAS_CONSUMO[UsoMoto.CIUDAD], ConsumoCiudad)
    assert isinstance(ESTRATEGIAS_CONSUMO[UsoMoto.CARRETERA], ConsumoCarretera)
    assert isinstance(ESTRATEGIAS_CONSUMO[UsoMoto.TRABAJO], ConsumoTrabajo)


def test_cada_estrategia_calcula_distinto_la_gasolina():
    ciudad = ConsumoCiudad().costo_gasolina(1000, 100, 15000)
    carretera = ConsumoCarretera().costo_gasolina(1000, 100, 15000)
    trabajo = ConsumoTrabajo().costo_gasolina(1000, 100, 15000)
    assert (carretera, ciudad, trabajo) == (142500, 172500, 180000)


class ConsumoFijo(EstrategiaConsumo):
    def factor(self) -> float:
        return 2.0

    def descripcion(self) -> str:
        return "Estrategia de prueba"


def test_la_calculadora_usa_la_estrategia_que_recibe_sin_cambiar_su_codigo():
    estrategias = {uso: ConsumoFijo() for uso in UsoMoto}
    calculadora = CalculadoraCostoReal(estrategias)
    perfil = PerfilUso(km_mes=1000, uso=UsoMoto.CIUDAD)
    la_moto = moto()
    costo = calculadora.calcular(la_moto, plan(la_moto.precio_cop), perfil, parametros())
    esperado = round(1000 / la_moto.consumo_km_galon * parametros().precio_galon_cop * 2.0)
    assert costo.gasolina_cop == esperado
