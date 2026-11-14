from dataclasses import dataclass, field

from app.domain.catalogo import CILINDRAJE_MAXIMO_A1, UsoMoto
from app.domain.excepciones import EntidadNoEncontradaError

TASA_MENSUAL_REFERENCIA = 0.0179


@dataclass(frozen=True)
class PerfilUso:
    km_mes: int
    uso: UsoMoto
    ganancia_diaria_cop: int = 0
    dias_trabajo_mes: int = 0

    def __post_init__(self) -> None:
        if self.km_mes < 0:
            raise ValueError("Los kilómetros al mes no pueden ser negativos")
        if self.ganancia_diaria_cop < 0 or self.dias_trabajo_mes < 0:
            raise ValueError("La ganancia y los días de trabajo no pueden ser negativos")
        if self.dias_trabajo_mes > 31:
            raise ValueError("Un mes no tiene más de 31 días")

    def ganancia_mensual(self) -> int:
        return self.ganancia_diaria_cop * self.dias_trabajo_mes


@dataclass(frozen=True)
class CostoMensual:
    cuota_credito_cop: int
    gasolina_cop: int
    soat_cop: int
    mantenimiento_cop: int
    impuesto_cop: int

    def total(self) -> int:
        return (
            self.cuota_credito_cop
            + self.gasolina_cop
            + self.soat_cop
            + self.mantenimiento_cop
            + self.impuesto_cop
        )


@dataclass(frozen=True)
class CostoAdquisicion:
    precio_lista_cop: int
    matricula_cop: int
    soat_cop: int
    impuesto_cop: int
    tramites_cop: int

    def total(self) -> int:
        return (
            self.precio_lista_cop
            + self.matricula_cop
            + self.soat_cop
            + self.impuesto_cop
            + self.tramites_cop
        )


@dataclass(frozen=True)
class TarifaSoat:
    cilindraje_min: int
    cilindraje_max: int
    valor_anual_cop: int

    def __post_init__(self) -> None:
        if self.cilindraje_min > self.cilindraje_max:
            raise ValueError("El cilindraje mínimo no puede ser mayor que el máximo")

    def aplica(self, cilindraje_cc: int) -> bool:
        return self.cilindraje_min <= cilindraje_cc <= self.cilindraje_max


@dataclass(kw_only=True)
class ParametrosCosto:
    id: int | None = None
    precio_galon_cop: int
    porcentaje_impuesto: float
    tarifas_soat: list[TarifaSoat] = field(default_factory=list)
    valor_matricula_cop: int = 0
    valor_tramites_cop: int = 0
    tasa_mensual: float = TASA_MENSUAL_REFERENCIA

    def __post_init__(self) -> None:
        if self.precio_galon_cop <= 0:
            raise ValueError("El precio del galón debe ser mayor que cero")
        if not 0 <= self.porcentaje_impuesto <= 100:
            raise ValueError("El porcentaje de impuesto debe estar entre 0 y 100")
        if self.valor_matricula_cop < 0 or self.valor_tramites_cop < 0:
            raise ValueError("La matrícula y los trámites no pueden ser negativos")
        if not 0 <= self.tasa_mensual < 1:
            raise ValueError("La tasa mensual debe estar entre 0 y 1")

    def soat_anual(self, cilindraje_cc: int) -> int:
        for tarifa in self.tarifas_soat:
            if tarifa.aplica(cilindraje_cc):
                return tarifa.valor_anual_cop
        raise EntidadNoEncontradaError(f"No hay tarifa de SOAT para {cilindraje_cc} cc")

    def soat_mensual(self, cilindraje_cc: int) -> int:
        return round(self.soat_anual(cilindraje_cc) / 12)

    def impuesto_anual(self, precio_cop: int, cilindraje_cc: int) -> int:
        if cilindraje_cc <= CILINDRAJE_MAXIMO_A1:
            return 0
        return round(precio_cop * self.porcentaje_impuesto / 100)

    def impuesto_mensual(self, precio_cop: int, cilindraje_cc: int) -> int:
        if cilindraje_cc <= CILINDRAJE_MAXIMO_A1:
            return 0
        return round(precio_cop * self.porcentaje_impuesto / 100 / 12)
