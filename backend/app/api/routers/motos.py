from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Response, status

from app.api.dependencias import (
    obtener_buscar_por_cuota,
    obtener_calcular_costo_real,
    obtener_listar_motos,
    obtener_obtener_moto,
)
from app.api.schemas.motos import (
    PATRON_SESION,
    CostoAdquisicionSalida,
    CostoMensualSalida,
    CostoRealEntrada,
    CostoRealSalida,
    FiltrosMotoEntrada,
    FinanciacionSalida,
    ModoTrabajoSalida,
    MotoDetalleSalida,
    MotoFinanciableSalida,
    MotoResumenSalida,
    PorCuotaEntrada,
    PorCuotaSalida,
)
from app.application.motos import (
    BuscarMotosPorCuota,
    CalcularCostoReal,
    ConsultaCostoReal,
    ConsultaPorCuota,
    ListarMotos,
    ObtenerMoto,
)
from app.domain.excepciones import CreditoInvalidoError, EntidadNoEncontradaError
from app.domain.puertos import FiltrosMoto

router = APIRouter(prefix="/motos", tags=["Catálogo"])

RESPUESTA_404: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {"description": "La moto no existe"}
}
IdMoto = Annotated[int, Path(ge=1, description="Identificador de la moto")]


def _no_encontrada(error: EntidadNoEncontradaError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.mensaje)


def _credito_invalido(error: CreditoInvalidoError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=error.mensaje)


@router.get("", response_model=list[MotoResumenSalida])
def listar_motos(
    filtros: Annotated[FiltrosMotoEntrada, Query()],
    caso_de_uso: Annotated[ListarMotos, Depends(obtener_listar_motos)],
) -> list[MotoResumenSalida]:
    motos = caso_de_uso.ejecutar(
        FiltrosMoto(
            marca_id=filtros.marca_id,
            tipo=filtros.tipo,
            categoria_licencia=filtros.licencia,
            precio_min=filtros.precio_min,
            precio_max=filtros.precio_max,
            cilindraje_min=filtros.cilindraje_min,
            cilindraje_max=filtros.cilindraje_max,
        )
    )
    return [MotoResumenSalida.desde_dominio(moto) for moto in motos]


@router.get("/por-cuota", response_model=PorCuotaSalida)
def buscar_por_cuota(
    entrada: Annotated[PorCuotaEntrada, Query()],
    respuesta: Response,
    caso_de_uso: Annotated[BuscarMotosPorCuota, Depends(obtener_buscar_por_cuota)],
    x_sesion_id: Annotated[str | None, Header(pattern=PATRON_SESION)] = None,
) -> PorCuotaSalida:
    sesion_id = x_sesion_id or uuid4().hex
    try:
        resultado = caso_de_uso.ejecutar(
            ConsultaPorCuota(
                cuota_maxima_cop=entrada.cuota_maxima_cop,
                cuota_inicial_cop=entrada.cuota_inicial_cop,
                plazo_meses=entrada.plazo_meses,
                categoria_licencia=entrada.licencia,
                uso=entrada.uso,
                marca_id=entrada.marca_id,
                sesion_id=sesion_id,
            )
        )
    except CreditoInvalidoError as error:
        raise _credito_invalido(error) from error
    respuesta.headers["X-Sesion-Id"] = sesion_id
    return PorCuotaSalida(
        busqueda_id=resultado.busqueda.id or 0,
        sesion_id=sesion_id,
        simulaciones_en_sesion=resultado.simulaciones_en_sesion,
        cuota_maxima_cop=entrada.cuota_maxima_cop,
        cuota_inicial_cop=entrada.cuota_inicial_cop,
        plazo_meses=entrada.plazo_meses,
        tasa_mensual=resultado.tasa_mensual,
        licencia=entrada.licencia,
        precio_maximo_cop=resultado.precio_maximo_cop,
        cantidad_resultados=len(resultado.motos),
        motos=[
            MotoFinanciableSalida(
                moto=MotoResumenSalida.desde_dominio(item.moto),
                cuota_inicial_cop=item.plan.cuota_inicial_cop,
                monto_financiado_cop=item.plan.monto_financiado(),
                cuota_mensual_cop=item.cuota_mensual_cop,
            )
            for item in resultado.motos
        ],
    )


@router.get("/{moto_id}", response_model=MotoDetalleSalida, responses=RESPUESTA_404)
def obtener_moto(
    moto_id: IdMoto,
    caso_de_uso: Annotated[ObtenerMoto, Depends(obtener_obtener_moto)],
) -> MotoDetalleSalida:
    try:
        moto = caso_de_uso.ejecutar(moto_id)
    except EntidadNoEncontradaError as error:
        raise _no_encontrada(error) from error
    return MotoDetalleSalida.desde_dominio(moto)


@router.get("/{moto_id}/costo-real", response_model=CostoRealSalida, responses=RESPUESTA_404)
def calcular_costo_real(
    moto_id: IdMoto,
    entrada: Annotated[CostoRealEntrada, Query()],
    caso_de_uso: Annotated[CalcularCostoReal, Depends(obtener_calcular_costo_real)],
) -> CostoRealSalida:
    try:
        resultado = caso_de_uso.ejecutar(
            ConsultaCostoReal(
                moto_id=moto_id,
                km_mes=entrada.km_mes,
                uso=entrada.uso,
                cuota_inicial_cop=entrada.cuota_inicial_cop,
                plazo_meses=entrada.plazo_meses,
                ganancia_diaria_cop=entrada.ganancia_diaria_cop,
                dias_trabajo_mes=entrada.dias_trabajo_mes,
            )
        )
    except EntidadNoEncontradaError as error:
        raise _no_encontrada(error) from error
    except CreditoInvalidoError as error:
        raise _credito_invalido(error) from error
    adquisicion = resultado.adquisicion
    mensual = resultado.mensual
    plan = resultado.plan
    trabajo = resultado.modo_trabajo
    return CostoRealSalida(
        moto=MotoResumenSalida.desde_dominio(resultado.moto),
        km_mes=entrada.km_mes,
        uso=entrada.uso,
        adquisicion=CostoAdquisicionSalida(
            precio_lista_cop=adquisicion.precio_lista_cop,
            matricula_cop=adquisicion.matricula_cop,
            soat_cop=adquisicion.soat_cop,
            impuesto_cop=adquisicion.impuesto_cop,
            tramites_cop=adquisicion.tramites_cop,
            total_cop=adquisicion.total(),
        ),
        financiacion=FinanciacionSalida(
            cuota_inicial_cop=plan.cuota_inicial_cop,
            monto_financiado_cop=plan.monto_financiado(),
            plazo_meses=plan.plazo_meses,
            tasa_mensual=plan.tasa_mensual,
            cuota_mensual_cop=plan.cuota_mensual(),
        ),
        mensual=CostoMensualSalida(
            cuota_credito_cop=mensual.cuota_credito_cop,
            gasolina_cop=mensual.gasolina_cop,
            soat_cop=mensual.soat_cop,
            mantenimiento_cop=mensual.mantenimiento_cop,
            impuesto_cop=mensual.impuesto_cop,
            total_cop=mensual.total(),
        ),
        modo_trabajo=(
            None
            if trabajo is None
            else ModoTrabajoSalida(
                ganancia_mensual_cop=trabajo.ganancia_mensual_cop,
                ganancia_neta_mensual_cop=trabajo.ganancia_neta_mensual_cop,
                meses_para_pagarse=trabajo.meses_para_pagarse,
            )
        ),
    )
