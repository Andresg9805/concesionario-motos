from datetime import date

from pydantic import BaseModel

from app.domain.catalogo import CategoriaLicencia
from app.domain.reportes import FilaRadar, ReporteVentas


class FilaRadarSalida(BaseModel):
    rango: str
    licencia: CategoriaLicencia
    busquedas: int
    sin_resultados: int
    promedio_resultados: float
    motos_en_stock: int

    @classmethod
    def desde_dominio(cls, fila: FilaRadar) -> "FilaRadarSalida":
        return cls(
            rango=fila.rango,
            licencia=fila.licencia,
            busquedas=fila.busquedas,
            sin_resultados=fila.sin_resultados,
            promedio_resultados=fila.promedio_resultados,
            motos_en_stock=fila.motos_en_stock,
        )


class RadarDemandaSalida(BaseModel):
    total_busquedas: int
    filas: list[FilaRadarSalida]


class VentaPorCategoriaSalida(BaseModel):
    categoria: str
    semana: date
    unidades: int
    ingresos_cop: int


class AccesorioMasVendidoSalida(BaseModel):
    nombre: str
    unidades: int
    ingresos_cop: int


class ReporteVentasSalida(BaseModel):
    pedidos: int
    ingresos_cop: int
    ticket_promedio_cop: int
    por_categoria_y_semana: list[VentaPorCategoriaSalida]
    mas_vendidos: list[AccesorioMasVendidoSalida]

    @classmethod
    def desde_dominio(cls, reporte: ReporteVentas) -> "ReporteVentasSalida":
        return cls(
            pedidos=reporte.pedidos,
            ingresos_cop=reporte.ingresos_cop,
            ticket_promedio_cop=reporte.ticket_promedio_cop,
            por_categoria_y_semana=[
                VentaPorCategoriaSalida(
                    categoria=v.categoria,
                    semana=v.semana,
                    unidades=v.unidades,
                    ingresos_cop=v.ingresos_cop,
                )
                for v in reporte.por_categoria_y_semana
            ],
            mas_vendidos=[
                AccesorioMasVendidoSalida(
                    nombre=a.nombre, unidades=a.unidades, ingresos_cop=a.ingresos_cop
                )
                for a in reporte.mas_vendidos
            ],
        )
