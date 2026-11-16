from dataclasses import dataclass, field
from datetime import date

from app.domain.catalogo import CategoriaLicencia

CUOTA_INICIAL_REFERENCIA_PCT = 10
PLAZO_REFERENCIA_MESES = 36


@dataclass(frozen=True)
class RangoCuota:
    orden: int
    nombre: str
    desde_cop: int
    hasta_cop: int | None


RANGOS_CUOTA: tuple[RangoCuota, ...] = (
    RangoCuota(1, "Menos de $300.000", 0, 300_000),
    RangoCuota(2, "$300.000 a $499.999", 300_000, 500_000),
    RangoCuota(3, "$500.000 a $799.999", 500_000, 800_000),
    RangoCuota(4, "$800.000 o más", 800_000, None),
)


@dataclass(frozen=True)
class FilaRadar:
    rango: str
    licencia: CategoriaLicencia
    busquedas: int
    sin_resultados: int
    promedio_resultados: float
    motos_en_stock: int


@dataclass(frozen=True)
class VentaPorCategoria:
    categoria: str
    semana: date
    unidades: int
    ingresos_cop: int


@dataclass(frozen=True)
class AccesorioMasVendido:
    nombre: str
    unidades: int
    ingresos_cop: int


@dataclass(frozen=True)
class ReporteVentas:
    pedidos: int
    ingresos_cop: int
    ticket_promedio_cop: int
    por_categoria_y_semana: list[VentaPorCategoria] = field(default_factory=list)
    mas_vendidos: list[AccesorioMasVendido] = field(default_factory=list)
