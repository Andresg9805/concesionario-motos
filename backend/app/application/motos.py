from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.catalogo import Busqueda, CategoriaLicencia, Marca, Moto, PlanCredito, UsoMoto
from app.domain.costo_real import CostoAdquisicion, CostoMensual, PerfilUso
from app.domain.estructuras.arbol_motos import ArbolMotosPorPrecio
from app.domain.excepciones import CreditoInvalidoError, EntidadNoEncontradaError
from app.domain.puertos import (
    FiltrosMoto,
    RepositorioBusquedas,
    RepositorioMarcas,
    RepositorioMotos,
    RepositorioParametros,
    RepositorioSimulaciones,
)
from app.domain.servicios import CalculadoraCostoReal

Reloj = Callable[[], datetime]


def reloj_utc() -> datetime:
    return datetime.now(UTC)


class ListarMarcas:
    def __init__(self, marcas: RepositorioMarcas) -> None:
        self._marcas = marcas

    def ejecutar(self) -> list[Marca]:
        return sorted(self._marcas.listar(), key=lambda marca: marca.id or 0)


class ListarMotos:
    def __init__(self, motos: RepositorioMotos) -> None:
        self._motos = motos

    def ejecutar(self, filtros: FiltrosMoto) -> list[Moto]:
        return sorted(self._motos.listar(filtros), key=lambda moto: moto.id or 0)


class ObtenerMoto:
    def __init__(self, motos: RepositorioMotos) -> None:
        self._motos = motos

    def ejecutar(self, moto_id: int) -> Moto:
        moto = self._motos.buscar_por_id(moto_id)
        if moto is None:
            raise EntidadNoEncontradaError(f"No existe una moto con id {moto_id}")
        return moto


@dataclass(frozen=True)
class ConsultaPorCuota:
    cuota_maxima_cop: int
    cuota_inicial_cop: int
    plazo_meses: int
    categoria_licencia: CategoriaLicencia
    uso: UsoMoto
    sesion_id: str
    marca_id: int | None = None


@dataclass(frozen=True)
class MotoFinanciable:
    moto: Moto
    plan: PlanCredito
    cuota_mensual_cop: int


@dataclass(frozen=True)
class ResultadoPorCuota:
    busqueda: Busqueda
    precio_maximo_cop: int
    tasa_mensual: float
    motos: list[MotoFinanciable]
    simulaciones_en_sesion: int


class BuscarMotosPorCuota:
    def __init__(
        self,
        motos: RepositorioMotos,
        parametros: RepositorioParametros,
        busquedas: RepositorioBusquedas,
        simulaciones: RepositorioSimulaciones,
        reloj: Reloj = reloj_utc,
    ) -> None:
        self._motos = motos
        self._parametros = parametros
        self._busquedas = busquedas
        self._simulaciones = simulaciones
        self._reloj = reloj

    def ejecutar(self, consulta: ConsultaPorCuota) -> ResultadoPorCuota:
        tasa = self._parametros.obtener().tasa_mensual
        precio_maximo = PlanCredito.precio_maximo_para_cuota(
            consulta.cuota_maxima_cop, consulta.cuota_inicial_cop, consulta.plazo_meses, tasa
        )
        filtros = FiltrosMoto(
            marca_id=consulta.marca_id,
            categoria_licencia=(
                CategoriaLicencia.A1
                if consulta.categoria_licencia == CategoriaLicencia.A1
                else None
            ),
        )
        arbol = ArbolMotosPorPrecio()
        for moto in self._motos.listar(filtros):
            if moto.apta_para(consulta.categoria_licencia):
                arbol.insertar(moto)
        financiables: list[MotoFinanciable] = []
        for moto in arbol.buscar_rango(0, precio_maximo):
            plan = PlanCredito(
                precio_cop=moto.precio_cop,
                cuota_inicial_cop=min(consulta.cuota_inicial_cop, moto.precio_cop),
                plazo_meses=consulta.plazo_meses,
                tasa_mensual=tasa,
            )
            cuota = plan.cuota_mensual()
            if cuota <= consulta.cuota_maxima_cop:
                financiables.append(MotoFinanciable(moto=moto, plan=plan, cuota_mensual_cop=cuota))
        busqueda = self._busquedas.guardar(
            Busqueda(
                fecha=self._reloj(),
                cuota_maxima_cop=consulta.cuota_maxima_cop,
                cuota_inicial_cop=consulta.cuota_inicial_cop,
                categoria_licencia=consulta.categoria_licencia,
                uso=consulta.uso,
                marca_id=consulta.marca_id,
                cantidad_resultados=len(financiables),
            )
        )
        simulacion = PlanCredito(
            precio_cop=precio_maximo,
            cuota_inicial_cop=consulta.cuota_inicial_cop,
            plazo_meses=consulta.plazo_meses,
            tasa_mensual=tasa,
        )
        en_sesion = self._simulaciones.apilar(consulta.sesion_id, simulacion)
        return ResultadoPorCuota(
            busqueda=busqueda,
            precio_maximo_cop=precio_maximo,
            tasa_mensual=tasa,
            motos=financiables,
            simulaciones_en_sesion=en_sesion,
        )


@dataclass(frozen=True)
class ConsultaCostoReal:
    moto_id: int
    km_mes: int
    uso: UsoMoto
    cuota_inicial_cop: int
    plazo_meses: int
    ganancia_diaria_cop: int = 0
    dias_trabajo_mes: int = 0


@dataclass(frozen=True)
class ModoTrabajo:
    ganancia_mensual_cop: int
    ganancia_neta_mensual_cop: int
    meses_para_pagarse: int | None


@dataclass(frozen=True)
class ResultadoCostoReal:
    moto: Moto
    plan: PlanCredito
    adquisicion: CostoAdquisicion
    mensual: CostoMensual
    modo_trabajo: ModoTrabajo | None


class CalcularCostoReal:
    def __init__(
        self,
        motos: RepositorioMotos,
        parametros: RepositorioParametros,
        calculadora: CalculadoraCostoReal | None = None,
    ) -> None:
        self._motos = motos
        self._parametros = parametros
        self._calculadora = calculadora or CalculadoraCostoReal()

    def ejecutar(self, consulta: ConsultaCostoReal) -> ResultadoCostoReal:
        moto = ObtenerMoto(self._motos).ejecutar(consulta.moto_id)
        parametros = self._parametros.obtener()
        plan = PlanCredito(
            precio_cop=moto.precio_cop,
            cuota_inicial_cop=consulta.cuota_inicial_cop,
            plazo_meses=consulta.plazo_meses,
            tasa_mensual=parametros.tasa_mensual,
        )
        perfil = PerfilUso(
            km_mes=consulta.km_mes,
            uso=consulta.uso,
            ganancia_diaria_cop=consulta.ganancia_diaria_cop,
            dias_trabajo_mes=consulta.dias_trabajo_mes,
        )
        mensual = self._calculadora.calcular(moto, plan, perfil, parametros)
        return ResultadoCostoReal(
            moto=moto,
            plan=plan,
            adquisicion=self._calculadora.costo_adquisicion(moto, parametros),
            mensual=mensual,
            modo_trabajo=self._modo_trabajo(mensual, perfil, plan),
        )

    def _modo_trabajo(
        self, mensual: CostoMensual, perfil: PerfilUso, plan: PlanCredito
    ) -> ModoTrabajo | None:
        ganancia = perfil.ganancia_mensual()
        if ganancia == 0:
            return None
        try:
            meses: int | None = self._calculadora.meses_para_pagarse(mensual, perfil, plan)
        except CreditoInvalidoError:
            meses = None
        return ModoTrabajo(
            ganancia_mensual_cop=ganancia,
            ganancia_neta_mensual_cop=ganancia - mensual.total(),
            meses_para_pagarse=meses,
        )
