import pytest

from app.domain.atencion import Rol, Usuario
from app.domain.catalogo import PlanCredito, UsoMoto
from app.domain.costo_real import ParametrosCosto, PerfilUso, TarifaSoat
from app.domain.excepciones import CreditoInvalidoError, SinAsesorDisponibleError
from app.domain.servicios import (
    ALFABETO_CODIGO,
    AsignadorAsesor,
    CalculadoraCostoReal,
    GeneradorCodigo,
)
from tests.domain import fabricas

calculadora = CalculadoraCostoReal()


def parametros() -> ParametrosCosto:
    return ParametrosCosto(
        precio_galon_cop=16_000,
        porcentaje_impuesto=1.5,
        tarifas_soat=[TarifaSoat(cilindraje_min=0, cilindraje_max=2000, valor_anual_cop=600_000)],
    )


def moto_ejemplo():
    return fabricas.moto(precio_cop=24_000_000)


def plan_ejemplo() -> PlanCredito:
    return PlanCredito(precio_cop=24_000_000, cuota_inicial_cop=0, plazo_meses=24, tasa_mensual=0)


@pytest.mark.parametrize(
    ("uso", "gasolina"),
    [(UsoMoto.CIUDAD, 245_333), (UsoMoto.CARRETERA, 202_667), (UsoMoto.TRABAJO, 256_000)],
)
def test_gasolina_segun_el_uso(uso, gasolina):
    perfil = PerfilUso(km_mes=1_200, uso=uso)
    costo = calculadora.calcular(moto_ejemplo(), plan_ejemplo(), perfil, parametros())
    assert costo.gasolina_cop == gasolina


def test_costo_real_completo():
    perfil = PerfilUso(km_mes=1_200, uso=UsoMoto.CIUDAD)
    costo = calculadora.calcular(moto_ejemplo(), plan_ejemplo(), perfil, parametros())
    assert costo.cuota_credito_cop == 1_000_000
    assert costo.soat_cop == 50_000
    assert costo.mantenimiento_cop == 72_000
    assert costo.impuesto_cop == 30_000
    assert costo.total() == 1_000_000 + 245_333 + 50_000 + 72_000 + 30_000


def test_plan_con_otro_precio_no_se_calcula():
    perfil = PerfilUso(km_mes=1_200, uso=UsoMoto.CIUDAD)
    with pytest.raises(CreditoInvalidoError):
        calculadora.calcular(moto_ejemplo(), fabricas.plan(), perfil, parametros())


def test_meses_para_pagarse_en_modo_trabajo():
    perfil = PerfilUso(
        km_mes=1_200, uso=UsoMoto.TRABAJO, ganancia_diaria_cop=80_000, dias_trabajo_mes=26
    )
    costo = calculadora.calcular(moto_ejemplo(), plan_ejemplo(), perfil, parametros())
    libre = 2_080_000 - (256_000 + 50_000 + 72_000 + 30_000)
    assert calculadora.meses_para_pagarse(costo, perfil, plan_ejemplo()) == -(-24_000_000 // libre)


def test_si_no_le_queda_nada_libre_la_moto_no_se_paga():
    perfil = PerfilUso(
        km_mes=1_200, uso=UsoMoto.TRABAJO, ganancia_diaria_cop=10_000, dias_trabajo_mes=10
    )
    costo = calculadora.calcular(moto_ejemplo(), plan_ejemplo(), perfil, parametros())
    with pytest.raises(CreditoInvalidoError):
        calculadora.meses_para_pagarse(costo, perfil, plan_ejemplo())


def asesor_con_id(id: int) -> Usuario:
    asesor = fabricas.asesor()
    asesor.id = id
    return asesor


def test_elige_al_asesor_con_menos_atenciones_abiertas():
    asesores = [asesor_con_id(1), asesor_con_id(2), asesor_con_id(3)]
    elegido = AsignadorAsesor().elegir(asesores, {1: 4, 2: 1, 3: 2})
    assert elegido.id == 2


def test_asesor_sin_atenciones_cuenta_como_cero():
    asesores = [asesor_con_id(1), asesor_con_id(2)]
    assert AsignadorAsesor().elegir(asesores, {1: 3}).id == 2


def test_en_empate_gana_el_de_menor_id():
    asesores = [asesor_con_id(5), asesor_con_id(2)]
    assert AsignadorAsesor().elegir(asesores, {5: 1, 2: 1}).id == 2


def test_sin_asesores_falla():
    with pytest.raises(SinAsesorDisponibleError):
        AsignadorAsesor().elegir([], {})


def test_usuarios_que_no_son_asesores_no_se_eligen():
    cliente = Usuario(id=9, nombre="C", correo="c@correo.com", hash_contrasena="h", rol=Rol.CLIENTE)
    with pytest.raises(SinAsesorDisponibleError):
        AsignadorAsesor().elegir([cliente], {})


def test_codigo_con_formato_cm_xxxx():
    codigo = GeneradorCodigo.nuevo_codigo()
    assert codigo.startswith("CM-")
    assert len(codigo) == 7
    assert all(letra in ALFABETO_CODIGO for letra in codigo[3:])


def test_codigo_sin_caracteres_que_se_confunden():
    codigos = "".join(GeneradorCodigo.nuevo_codigo()[3:] for _ in range(500))
    assert not set(codigos) & set("O0I1")
