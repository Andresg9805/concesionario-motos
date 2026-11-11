from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from app.domain.excepciones import CreditoInvalidoError

MARCAS_PERMITIDAS = ("Honda", "Kawasaki", "Yamaha")
CILINDRAJE_MAXIMO_A1 = 125


class TipoMoto(StrEnum):
    NAKED = "NAKED"
    DOBLE_PROPOSITO = "DOBLE_PROPOSITO"
    DEPORTIVA = "DEPORTIVA"
    TRAIL = "TRAIL"


class CategoriaLicencia(StrEnum):
    A1 = "A1"
    A2 = "A2"


class UsoMoto(StrEnum):
    CIUDAD = "CIUDAD"
    CARRETERA = "CARRETERA"
    TRABAJO = "TRABAJO"


@dataclass(kw_only=True)
class Marca:
    id: int | None = None
    nombre: str
    color_hex: str
    descripcion: str = ""

    def __post_init__(self) -> None:
        if self.nombre not in MARCAS_PERMITIDAS:
            raise ValueError(f"La marca {self.nombre} no se vende en Candela Motors")


@dataclass(frozen=True)
class TasaCambio:
    valor: float
    fecha: date

    def __post_init__(self) -> None:
        if self.valor <= 0:
            raise ValueError("La TRM debe ser mayor que cero")


@dataclass(kw_only=True)
class Moto:
    id: int | None = None
    marca: Marca
    modelo: str
    anio: int
    cilindraje_cc: int
    tipo: TipoMoto
    categoria_licencia: CategoriaLicencia | None = None
    precio_cop: int
    stock: int = 0
    consumo_km_galon: float
    costo_mantenimiento_km_cop: int
    descripcion: str = ""
    imagen_url: str = ""

    def __post_init__(self) -> None:
        if self.cilindraje_cc <= 0:
            raise ValueError("El cilindraje debe ser mayor que cero")
        if self.precio_cop <= 0:
            raise ValueError("El precio debe ser mayor que cero")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")
        if self.consumo_km_galon <= 0:
            raise ValueError("El consumo debe ser mayor que cero")
        categoria = Moto.categoria_por_cilindraje(self.cilindraje_cc)
        if self.categoria_licencia is None:
            self.categoria_licencia = categoria
        elif self.categoria_licencia != categoria:
            raise ValueError(
                f"Una moto de {self.cilindraje_cc} cc es {categoria.value}, "
                f"no {self.categoria_licencia.value}"
            )

    @staticmethod
    def categoria_por_cilindraje(cilindraje_cc: int) -> CategoriaLicencia:
        if cilindraje_cc <= CILINDRAJE_MAXIMO_A1:
            return CategoriaLicencia.A1
        return CategoriaLicencia.A2

    def esta_disponible(self) -> bool:
        return self.stock > 0

    def apta_para(self, licencia: CategoriaLicencia) -> bool:
        if licencia == CategoriaLicencia.A2:
            return True
        return self.categoria_licencia == CategoriaLicencia.A1

    def precio_en_usd(self, trm: TasaCambio) -> float:
        return round(self.precio_cop / trm.valor, 2)


@dataclass(frozen=True)
class PlanCredito:
    precio_cop: int
    cuota_inicial_cop: int
    plazo_meses: int
    tasa_mensual: float

    def __post_init__(self) -> None:
        PlanCredito._validar(self.plazo_meses, self.tasa_mensual, self.cuota_inicial_cop)
        if self.precio_cop <= 0:
            raise CreditoInvalidoError("El precio debe ser mayor que cero")
        if self.cuota_inicial_cop > self.precio_cop:
            raise CreditoInvalidoError("La cuota inicial no puede ser mayor que el precio")

    @staticmethod
    def _validar(plazo_meses: int, tasa_mensual: float, cuota_inicial_cop: int) -> None:
        if plazo_meses <= 0:
            raise CreditoInvalidoError("El plazo debe ser de al menos un mes")
        if tasa_mensual < 0:
            raise CreditoInvalidoError("La tasa no puede ser negativa")
        if cuota_inicial_cop < 0:
            raise CreditoInvalidoError("La cuota inicial no puede ser negativa")

    def monto_financiado(self) -> int:
        return self.precio_cop - self.cuota_inicial_cop

    def cuota_mensual(self) -> int:
        monto = self.monto_financiado()
        if self.tasa_mensual == 0:
            return round(monto / self.plazo_meses)
        i = self.tasa_mensual
        return round(monto * i / (1 - (1 + i) ** -self.plazo_meses))

    @staticmethod
    def precio_maximo_para_cuota(cuota: int, cuota_inicial: int, plazo: int, tasa: float) -> int:
        PlanCredito._validar(plazo, tasa, cuota_inicial)
        if cuota <= 0:
            raise CreditoInvalidoError("La cuota debe ser mayor que cero")
        if tasa == 0:
            capital = float(cuota * plazo)
        else:
            capital = cuota * (1 - (1 + tasa) ** -plazo) / tasa
        return int(capital) + cuota_inicial


@dataclass(kw_only=True)
class Busqueda:
    id: int | None = None
    fecha: datetime
    cuota_maxima_cop: int
    cuota_inicial_cop: int
    categoria_licencia: CategoriaLicencia
    uso: UsoMoto
    marca_id: int | None = None
    cantidad_resultados: int = 0
