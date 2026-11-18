from abc import ABC, abstractmethod

from app.domain.catalogo import UsoMoto


class EstrategiaConsumo(ABC):
    @abstractmethod
    def factor(self) -> float: ...

    @abstractmethod
    def descripcion(self) -> str: ...

    def costo_gasolina(self, km_mes: int, consumo_km_galon: float, precio_galon_cop: int) -> int:
        galones = km_mes / consumo_km_galon
        return round(galones * precio_galon_cop * self.factor())


class ConsumoCiudad(EstrategiaConsumo):
    def factor(self) -> float:
        return 1.15

    def descripcion(self) -> str:
        return "Trancones y semáforos: gasta un 15 % más de lo que dice la ficha"


class ConsumoCarretera(EstrategiaConsumo):
    def factor(self) -> float:
        return 0.95

    def descripcion(self) -> str:
        return "Velocidad constante: gasta un 5 % menos de lo que dice la ficha"


class ConsumoTrabajo(EstrategiaConsumo):
    def factor(self) -> float:
        return 1.20

    def descripcion(self) -> str:
        return "Domicilios con muchas paradas: gasta un 20 % más de lo que dice la ficha"


ESTRATEGIAS_CONSUMO: dict[UsoMoto, EstrategiaConsumo] = {
    UsoMoto.CIUDAD: ConsumoCiudad(),
    UsoMoto.CARRETERA: ConsumoCarretera(),
    UsoMoto.TRABAJO: ConsumoTrabajo(),
}
