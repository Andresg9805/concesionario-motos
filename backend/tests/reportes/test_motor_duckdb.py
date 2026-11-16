from dataclasses import replace
from datetime import datetime, timedelta

from app.domain.catalogo import Busqueda, CategoriaLicencia, UsoMoto
from app.domain.tienda import CategoriaAccesorio, ItemPedido, Pedido
from app.infrastructure.db.repositorios.conversiones import ZONA_COLOMBIA
from app.infrastructure.reportes.duckdb_reportes import MotorReportesDuckDB, cuota_estimada
from tests.domain import fabricas

TASA = 0.0179
LUNES = datetime(2026, 11, 9, 10, 0, tzinfo=ZONA_COLOMBIA)


def busqueda(cuota: int, licencia: str = "A2", resultados: int = 2) -> Busqueda:
    return Busqueda(
        fecha=LUNES,
        cuota_maxima_cop=cuota,
        cuota_inicial_cop=0,
        categoria_licencia=CategoriaLicencia(licencia),
        uso=UsoMoto.CIUDAD,
        cantidad_resultados=resultados,
    )


def pedido_pagado(id: int, cantidad: int, dias: int = 0, accesorio=None) -> Pedido:
    usuario = fabricas.cliente_usuario()
    item = ItemPedido.desde_accesorio(accesorio or fabricas.accesorio(), cantidad)
    pedido = Pedido.crear(
        usuario, fabricas.direccion(usuario), [item], LUNES + timedelta(days=dias)
    )
    pedido.marcar_pagado()
    return replace(pedido, id=id)


def test_el_radar_agrupa_por_rango_de_cuota_y_licencia():
    busquedas = [busqueda(250_000), busqueda(280_000), busqueda(290_000, resultados=0)]
    busquedas.append(busqueda(600_000, licencia="A1"))

    filas = MotorReportesDuckDB().radar_demanda(busquedas, [], TASA)

    primera = filas[0]
    assert primera.rango == "Menos de $300.000"
    assert primera.licencia == CategoriaLicencia.A2
    assert primera.busquedas == 3
    assert primera.sin_resultados == 1
    assert primera.promedio_resultados == 1.3
    assert (filas[1].rango, filas[1].licencia, filas[1].busquedas) == (
        "$500.000 a $799.999",
        CategoriaLicencia.A1,
        1,
    )


def test_el_radar_cuenta_las_motos_en_stock_que_caben_en_la_cuota():
    barata = fabricas.moto(cilindraje_cc=150, precio_cop=8_000_000, stock=2)
    cara = fabricas.moto(cilindraje_cc=650, precio_cop=40_000_000, stock=1)
    agotada = fabricas.moto(cilindraje_cc=125, precio_cop=7_000_000, stock=0)
    assert cuota_estimada(barata, TASA) < 300_000 < cuota_estimada(cara, TASA)

    [fila] = MotorReportesDuckDB().radar_demanda([busqueda(299_000)], [barata, cara, agotada], TASA)

    assert fila.motos_en_stock == 1


def test_con_licencia_a1_solo_cuentan_las_motos_a1():
    a1 = fabricas.moto(cilindraje_cc=125, precio_cop=7_000_000, stock=1)
    a2 = fabricas.moto(cilindraje_cc=150, precio_cop=7_000_000, stock=1)
    assert cuota_estimada(a2, TASA) < 290_000

    [fila] = MotorReportesDuckDB().radar_demanda([busqueda(290_000, "A1")], [a1, a2], TASA)

    assert fila.motos_en_stock == 1


def test_el_radar_sin_busquedas_esta_vacio():
    assert MotorReportesDuckDB().radar_demanda([], [fabricas.moto()], TASA) == []


def test_ventas_suma_ingresos_y_calcula_el_ticket_promedio():
    reporte = MotorReportesDuckDB().ventas_accesorios(
        [pedido_pagado(1, cantidad=2), pedido_pagado(2, cantidad=1)]
    )

    assert reporte.pedidos == 2
    assert reporte.ingresos_cop == 750_000
    assert reporte.ticket_promedio_cop == 375_000
    assert reporte.mas_vendidos[0].nombre == "Casco integral"
    assert reporte.mas_vendidos[0].unidades == 3


def test_ventas_se_agrupan_por_categoria_y_semana():
    chaqueta = replace(
        fabricas.accesorio(precio_cop=480_000),
        id=11,
        nombre="Chaqueta",
        categoria=CategoriaAccesorio.CHAQUETA,
    )
    pedidos = [
        pedido_pagado(1, cantidad=1),
        pedido_pagado(2, cantidad=1, dias=2),
        pedido_pagado(3, cantidad=1, dias=7, accesorio=chaqueta),
    ]

    reporte = MotorReportesDuckDB().ventas_accesorios(pedidos)

    semanas = [
        (v.categoria, v.semana.isoformat(), v.unidades) for v in reporte.por_categoria_y_semana
    ]
    assert semanas == [("CASCO", "2026-11-09", 2), ("CHAQUETA", "2026-11-16", 1)]


def test_sin_ventas_todo_queda_en_cero():
    reporte = MotorReportesDuckDB().ventas_accesorios([])

    assert (reporte.pedidos, reporte.ingresos_cop, reporte.ticket_promedio_cop) == (0, 0, 0)
    assert reporte.por_categoria_y_semana == []
    assert reporte.mas_vendidos == []
