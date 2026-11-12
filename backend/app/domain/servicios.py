import math
import secrets

from app.domain.atencion import Usuario
from app.domain.catalogo import Moto, PlanCredito, UsoMoto
from app.domain.costo_real import CostoAdquisicion, CostoMensual, ParametrosCosto, PerfilUso
from app.domain.excepciones import CreditoInvalidoError, SinAsesorDisponibleError

FACTORES_CONSUMO: dict[UsoMoto, float] = {
    UsoMoto.CIUDAD: 1.15,
    UsoMoto.CARRETERA: 0.95,
    UsoMoto.TRABAJO: 1.20,
}

ALFABETO_CODIGO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class CalculadoraCostoReal:
    def calcular(
        self,
        moto: Moto,
        plan: PlanCredito,
        perfil: PerfilUso,
        parametros: ParametrosCosto,
    ) -> CostoMensual:
        if plan.precio_cop != moto.precio_cop:
            raise CreditoInvalidoError("El plan de crédito debe usar el precio de la moto")
        galones = perfil.km_mes / moto.consumo_km_galon
        gasolina = round(galones * parametros.precio_galon_cop * FACTORES_CONSUMO[perfil.uso])
        return CostoMensual(
            cuota_credito_cop=plan.cuota_mensual(),
            gasolina_cop=gasolina,
            soat_cop=parametros.soat_mensual(moto.cilindraje_cc),
            mantenimiento_cop=perfil.km_mes * moto.costo_mantenimiento_km_cop,
            impuesto_cop=parametros.impuesto_mensual(moto.precio_cop, moto.cilindraje_cc),
        )

    def costo_adquisicion(self, moto: Moto, parametros: ParametrosCosto) -> CostoAdquisicion:
        return CostoAdquisicion(
            precio_lista_cop=moto.precio_cop,
            matricula_cop=parametros.valor_matricula_cop,
            soat_cop=parametros.soat_anual(moto.cilindraje_cc),
            impuesto_cop=parametros.impuesto_anual(moto.precio_cop, moto.cilindraje_cc),
            tramites_cop=parametros.valor_tramites_cop,
        )

    def meses_para_pagarse(self, costo: CostoMensual, perfil: PerfilUso, plan: PlanCredito) -> int:
        gastos_de_uso = costo.total() - costo.cuota_credito_cop
        libre_al_mes = perfil.ganancia_mensual() - gastos_de_uso
        if libre_al_mes <= 0:
            raise CreditoInvalidoError("Con esa ganancia la moto no alcanza a pagarse")
        total_moto = plan.cuota_inicial_cop + plan.cuota_mensual() * plan.plazo_meses
        return math.ceil(total_moto / libre_al_mes)


class AsignadorAsesor:
    def elegir(self, asesores: list[Usuario], abiertas_por_asesor: dict[int, int]) -> Usuario:
        candidatos = [asesor for asesor in asesores if asesor.es_asesor()]
        if not candidatos:
            raise SinAsesorDisponibleError("No hay asesores disponibles para esta marca")
        return min(
            candidatos,
            key=lambda asesor: (abiertas_por_asesor.get(asesor.id or 0, 0), asesor.id or 0),
        )


class GeneradorCodigo:
    @staticmethod
    def nuevo_codigo() -> str:
        return "CM-" + "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(4))
