import duckdb

from app.domain.catalogo import Busqueda, CategoriaLicencia, Moto, PlanCredito
from app.domain.puertos import MotorReportes
from app.domain.reportes import (
    CUOTA_INICIAL_REFERENCIA_PCT,
    PLAZO_REFERENCIA_MESES,
    RANGOS_CUOTA,
    AccesorioMasVendido,
    FilaRadar,
    ReporteVentas,
    VentaPorCategoria,
)
from app.domain.tienda import Pedido
from app.infrastructure.db.repositorios.conversiones import fecha_a_bd

CONSULTA_RADAR = """
WITH agrupadas AS (
    SELECT r.orden, r.nombre, r.hasta, b.licencia,
           COUNT(*) AS busquedas,
           SUM(CASE WHEN b.resultados = 0 THEN 1 ELSE 0 END) AS sin_resultados,
           ROUND(AVG(b.resultados), 1) AS promedio_resultados
    FROM busquedas b
    JOIN rangos r
      ON b.cuota_maxima >= r.desde AND (r.hasta IS NULL OR b.cuota_maxima < r.hasta)
    GROUP BY r.orden, r.nombre, r.hasta, b.licencia
)
SELECT a.nombre, a.licencia, a.busquedas, a.sin_resultados, a.promedio_resultados,
       (SELECT COUNT(*) FROM motos m
         WHERE m.stock > 0
           AND (a.licencia = 'A2' OR m.licencia = 'A1')
           AND (a.hasta IS NULL OR m.cuota_estimada < a.hasta)) AS motos_en_stock
FROM agrupadas a
ORDER BY a.busquedas DESC, a.orden, a.licencia
"""

CONSULTA_TOTALES = """
SELECT COUNT(DISTINCT pedido_id), COALESCE(SUM(cantidad * precio_unitario), 0)
FROM ventas
"""

CONSULTA_POR_CATEGORIA = """
SELECT categoria, CAST(date_trunc('week', fecha) AS DATE) AS semana,
       SUM(cantidad) AS unidades, SUM(cantidad * precio_unitario) AS ingresos
FROM ventas
GROUP BY categoria, semana
ORDER BY semana, ingresos DESC, categoria
"""

CONSULTA_MAS_VENDIDOS = """
SELECT accesorio, SUM(cantidad) AS unidades, SUM(cantidad * precio_unitario) AS ingresos
FROM ventas
GROUP BY accesorio
ORDER BY unidades DESC, ingresos DESC, accesorio
LIMIT 5
"""


def cuota_estimada(moto: Moto, tasa_mensual: float) -> int:
    inicial = moto.precio_cop * CUOTA_INICIAL_REFERENCIA_PCT // 100
    plan = PlanCredito(
        precio_cop=moto.precio_cop,
        cuota_inicial_cop=inicial,
        plazo_meses=PLAZO_REFERENCIA_MESES,
        tasa_mensual=tasa_mensual,
    )
    return plan.cuota_mensual()


class MotorReportesDuckDB(MotorReportes):
    def radar_demanda(
        self, busquedas: list[Busqueda], motos: list[Moto], tasa_mensual: float
    ) -> list[FilaRadar]:
        con = duckdb.connect()
        try:
            con.execute(
                "CREATE TABLE rangos (orden INTEGER, nombre VARCHAR, desde BIGINT, hasta BIGINT)"
            )
            con.executemany(
                "INSERT INTO rangos VALUES (?, ?, ?, ?)",
                [(r.orden, r.nombre, r.desde_cop, r.hasta_cop) for r in RANGOS_CUOTA],
            )
            con.execute(
                "CREATE TABLE busquedas (cuota_maxima BIGINT, licencia VARCHAR, resultados INTEGER)"
            )
            if busquedas:
                con.executemany(
                    "INSERT INTO busquedas VALUES (?, ?, ?)",
                    [
                        (b.cuota_maxima_cop, b.categoria_licencia.value, b.cantidad_resultados)
                        for b in busquedas
                    ],
                )
            con.execute(
                "CREATE TABLE motos (licencia VARCHAR, stock INTEGER, cuota_estimada BIGINT)"
            )
            if motos:
                con.executemany(
                    "INSERT INTO motos VALUES (?, ?, ?)",
                    [
                        (
                            (m.categoria_licencia or CategoriaLicencia.A2).value,
                            m.stock,
                            cuota_estimada(m, tasa_mensual),
                        )
                        for m in motos
                    ],
                )
            filas = con.execute(CONSULTA_RADAR).fetchall()
        finally:
            con.close()
        return [
            FilaRadar(
                rango=nombre,
                licencia=CategoriaLicencia(licencia),
                busquedas=int(cantidad),
                sin_resultados=int(sin_resultados),
                promedio_resultados=float(promedio),
                motos_en_stock=int(en_stock),
            )
            for nombre, licencia, cantidad, sin_resultados, promedio, en_stock in filas
        ]

    def ventas_accesorios(self, pedidos: list[Pedido]) -> ReporteVentas:
        con = duckdb.connect()
        try:
            con.execute(
                "CREATE TABLE ventas (pedido_id INTEGER, fecha TIMESTAMP, categoria VARCHAR, "
                "accesorio VARCHAR, cantidad INTEGER, precio_unitario BIGINT)"
            )
            filas_ventas = [
                (
                    pedido.id,
                    fecha_a_bd(pedido.creado_en),
                    item.accesorio.categoria.value,
                    item.accesorio.nombre,
                    item.cantidad,
                    item.precio_unitario_cop,
                )
                for pedido in pedidos
                for item in pedido.items
            ]
            if filas_ventas:
                con.executemany("INSERT INTO ventas VALUES (?, ?, ?, ?, ?, ?)", filas_ventas)
            cantidad_pedidos, ingresos = con.execute(CONSULTA_TOTALES).fetchone() or (0, 0)
            por_categoria = con.execute(CONSULTA_POR_CATEGORIA).fetchall()
            mas_vendidos = con.execute(CONSULTA_MAS_VENDIDOS).fetchall()
        finally:
            con.close()
        cantidad_pedidos = int(cantidad_pedidos)
        ingresos = int(ingresos)
        return ReporteVentas(
            pedidos=cantidad_pedidos,
            ingresos_cop=ingresos,
            ticket_promedio_cop=ingresos // cantidad_pedidos if cantidad_pedidos else 0,
            por_categoria_y_semana=[
                VentaPorCategoria(
                    categoria=categoria,
                    semana=semana,
                    unidades=int(unidades),
                    ingresos_cop=int(ingresos_semana),
                )
                for categoria, semana, unidades, ingresos_semana in por_categoria
            ],
            mas_vendidos=[
                AccesorioMasVendido(nombre=nombre, unidades=int(unidades), ingresos_cop=int(total))
                for nombre, unidades, total in mas_vendidos
            ],
        )
