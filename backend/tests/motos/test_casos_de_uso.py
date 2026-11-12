from collections import Counter

import pytest

from app.application.motos import (
    CalcularCostoReal,
    ConsultaCostoReal,
    ConsultaPorCuota,
    ListarMotos,
    ObtenerMoto,
)
from app.domain.catalogo import CategoriaLicencia, PlanCredito, TipoMoto, UsoMoto
from app.domain.excepciones import CreditoInvalidoError, EntidadNoEncontradaError
from app.domain.puertos import FiltrosMoto
from tests.motos.conftest import AHORA


def consulta(**cambios):
    datos = {
        "cuota_maxima_cop": 350_000,
        "cuota_inicial_cop": 1_000_000,
        "plazo_meses": 36,
        "categoria_licencia": CategoriaLicencia.A2,
        "uso": UsoMoto.CIUDAD,
        "sesion_id": "sesion-prueba-01",
    }
    datos.update(cambios)
    return ConsultaPorCuota(**datos)


def test_datos_de_prueba_tienen_22_motos_de_las_tres_marcas(motos):
    catalogo = motos.listar(FiltrosMoto())
    assert len(catalogo) == 22
    assert Counter(moto.marca.nombre for moto in catalogo) == {
        "Honda": 8,
        "Kawasaki": 7,
        "Yamaha": 7,
    }
    assert {moto.tipo for moto in catalogo} == set(TipoMoto)


@pytest.mark.parametrize("tipo", list(TipoMoto))
def test_filtrar_por_tipo_solo_devuelve_ese_tipo(motos, tipo):
    resultado = ListarMotos(motos).ejecutar(FiltrosMoto(tipo=tipo))
    assert resultado
    assert all(moto.tipo == tipo for moto in resultado)


def test_filtrar_por_cilindraje_y_precio(motos):
    resultado = ListarMotos(motos).ejecutar(
        FiltrosMoto(cilindraje_min=150, cilindraje_max=300, precio_max=15_000_000)
    )
    assert resultado
    assert all(150 <= moto.cilindraje_cc <= 300 for moto in resultado)
    assert all(moto.precio_cop <= 15_000_000 for moto in resultado)


def test_obtener_moto_inexistente_lanza_error(motos):
    with pytest.raises(EntidadNoEncontradaError):
        ObtenerMoto(motos).ejecutar(999)


def test_por_cuota_respeta_cuota_maxima_y_precio_maximo(buscar_por_cuota, parametros):
    resultado = buscar_por_cuota.ejecutar(consulta())
    tasa = parametros.obtener().tasa_mensual
    esperado = PlanCredito.precio_maximo_para_cuota(350_000, 1_000_000, 36, tasa)
    assert resultado.precio_maximo_cop == esperado
    assert resultado.motos
    assert all(item.cuota_mensual_cop <= 350_000 for item in resultado.motos)
    assert all(item.moto.precio_cop <= esperado for item in resultado.motos)
    precios = [item.moto.precio_cop for item in resultado.motos]
    assert precios == sorted(precios)


def test_por_cuota_con_licencia_a1_excluye_motos_de_mas_de_125_cc(buscar_por_cuota):
    resultado = buscar_por_cuota.ejecutar(
        consulta(cuota_maxima_cop=2_000_000, categoria_licencia=CategoriaLicencia.A1)
    )
    assert resultado.motos
    assert all(item.moto.cilindraje_cc <= 125 for item in resultado.motos)


def test_por_cuota_filtra_por_marca(buscar_por_cuota):
    resultado = buscar_por_cuota.ejecutar(consulta(cuota_maxima_cop=3_000_000, marca_id=3))
    assert len(resultado.motos) == 7
    assert {item.moto.marca.nombre for item in resultado.motos} == {"Yamaha"}


def test_por_cuota_guarda_la_busqueda_sin_datos_personales(buscar_por_cuota, busquedas):
    resultado = buscar_por_cuota.ejecutar(consulta(marca_id=1))
    guardadas = busquedas.listar()
    assert len(guardadas) == 1
    busqueda = guardadas[0]
    assert busqueda.id == resultado.busqueda.id == 1
    assert busqueda.fecha == AHORA
    assert busqueda.cuota_maxima_cop == 350_000
    assert busqueda.cuota_inicial_cop == 1_000_000
    assert busqueda.categoria_licencia == CategoriaLicencia.A2
    assert busqueda.marca_id == 1
    assert busqueda.cantidad_resultados == len(resultado.motos)


def test_por_cuota_apila_la_simulacion_por_sesion(buscar_por_cuota, simulaciones):
    buscar_por_cuota.ejecutar(consulta())
    segunda = buscar_por_cuota.ejecutar(consulta(cuota_maxima_cop=500_000, plazo_meses=48))
    otra = buscar_por_cuota.ejecutar(consulta(sesion_id="otra-sesion-02"))
    assert segunda.simulaciones_en_sesion == 2
    assert otra.simulaciones_en_sesion == 1
    ultima = simulaciones.ultima("sesion-prueba-01")
    assert ultima is not None
    assert ultima.plazo_meses == 48
    assert ultima.precio_cop == segunda.precio_maximo_cop
    assert simulaciones.cantidad("sin-busquedas-03") == 0


def test_costo_real_suma_adquisicion_y_costo_mensual(motos, parametros):
    resultado = CalcularCostoReal(motos, parametros).ejecutar(
        ConsultaCostoReal(
            moto_id=14,
            km_mes=800,
            uso=UsoMoto.CIUDAD,
            cuota_inicial_cop=5_000_000,
            plazo_meses=24,
        )
    )
    datos = parametros.obtener()
    adquisicion = resultado.adquisicion
    assert resultado.moto.modelo == "Ninja 400"
    assert adquisicion.precio_lista_cop == 35_990_000
    assert adquisicion.matricula_cop == datos.valor_matricula_cop
    assert adquisicion.tramites_cop == datos.valor_tramites_cop
    assert adquisicion.soat_cop == datos.soat_anual(399)
    assert adquisicion.impuesto_cop == round(35_990_000 * datos.porcentaje_impuesto / 100)
    assert adquisicion.total() == (
        35_990_000
        + datos.valor_matricula_cop
        + datos.soat_anual(399)
        + adquisicion.impuesto_cop
        + datos.valor_tramites_cop
    )
    assert resultado.mensual.cuota_credito_cop == resultado.plan.cuota_mensual()
    assert resultado.modo_trabajo is None


def test_costo_real_moto_a1_no_paga_impuesto(motos, parametros):
    resultado = CalcularCostoReal(motos, parametros).ejecutar(
        ConsultaCostoReal(
            moto_id=1, km_mes=600, uso=UsoMoto.TRABAJO, cuota_inicial_cop=0, plazo_meses=36
        )
    )
    assert resultado.adquisicion.impuesto_cop == 0
    assert resultado.mensual.impuesto_cop == 0


def test_costo_real_en_modo_trabajo_calcula_meses(motos, parametros):
    resultado = CalcularCostoReal(motos, parametros).ejecutar(
        ConsultaCostoReal(
            moto_id=1,
            km_mes=2_000,
            uso=UsoMoto.TRABAJO,
            cuota_inicial_cop=1_000_000,
            plazo_meses=36,
            ganancia_diaria_cop=80_000,
            dias_trabajo_mes=26,
        )
    )
    trabajo = resultado.modo_trabajo
    assert trabajo is not None
    assert trabajo.ganancia_mensual_cop == 2_080_000
    assert trabajo.ganancia_neta_mensual_cop == 2_080_000 - resultado.mensual.total()
    assert trabajo.meses_para_pagarse is not None and trabajo.meses_para_pagarse > 0


def test_costo_real_con_cuota_inicial_mayor_al_precio_falla(motos, parametros):
    with pytest.raises(CreditoInvalidoError):
        CalcularCostoReal(motos, parametros).ejecutar(
            ConsultaCostoReal(
                moto_id=1,
                km_mes=800,
                uso=UsoMoto.CIUDAD,
                cuota_inicial_cop=99_000_000,
                plazo_meses=36,
            )
        )
