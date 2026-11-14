from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.api.dependencias import (
    obtener_consultar_seguimiento,
    obtener_solicitar_cotizacion,
    obtener_solicitar_test_drive,
)
from app.api.schemas.atencion import AtencionSalida, CotizacionEntrada, TestDriveEntrada
from app.application.atencion import (
    ConsultarSeguimiento,
    DatosContacto,
    SolicitarCotizacion,
    SolicitarTestDrive,
)
from app.domain.excepciones import (
    CreditoInvalidoError,
    DominioError,
    EntidadNoEncontradaError,
    SinAsesorDisponibleError,
)

router = APIRouter(tags=["Atención personalizada"])

RESPUESTAS_SOLICITUD: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {"description": "La moto no existe"},
    status.HTTP_409_CONFLICT: {"description": "No hay asesores de esa marca"},
}

ESTADOS_POR_ERROR: dict[type[DominioError], int] = {
    EntidadNoEncontradaError: status.HTTP_404_NOT_FOUND,
    SinAsesorDisponibleError: status.HTTP_409_CONFLICT,
    CreditoInvalidoError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


def _contacto(entrada: TestDriveEntrada) -> DatosContacto:
    return DatosContacto(nombre=entrada.nombre, correo=entrada.correo, celular=entrada.celular)


def _error_http(error: DominioError) -> HTTPException:
    return HTTPException(status_code=ESTADOS_POR_ERROR[type(error)], detail=error.mensaje)


@router.post(
    "/cotizaciones",
    status_code=status.HTTP_201_CREATED,
    response_model=AtencionSalida,
    responses=RESPUESTAS_SOLICITUD,
)
def solicitar_cotizacion(
    entrada: CotizacionEntrada,
    caso_de_uso: Annotated[SolicitarCotizacion, Depends(obtener_solicitar_cotizacion)],
) -> AtencionSalida:
    try:
        cotizacion = caso_de_uso.ejecutar(
            entrada.moto_id, _contacto(entrada), entrada.cuota_inicial_cop, entrada.plazo_meses
        )
    except (EntidadNoEncontradaError, SinAsesorDisponibleError, CreditoInvalidoError) as error:
        raise _error_http(error) from error
    return AtencionSalida.desde_dominio(cotizacion)


@router.post(
    "/test-drives",
    status_code=status.HTTP_201_CREATED,
    response_model=AtencionSalida,
    responses=RESPUESTAS_SOLICITUD,
)
def solicitar_test_drive(
    entrada: TestDriveEntrada,
    caso_de_uso: Annotated[SolicitarTestDrive, Depends(obtener_solicitar_test_drive)],
) -> AtencionSalida:
    try:
        test_drive = caso_de_uso.ejecutar(entrada.moto_id, _contacto(entrada))
    except (EntidadNoEncontradaError, SinAsesorDisponibleError) as error:
        raise _error_http(error) from error
    return AtencionSalida.desde_dominio(test_drive)


@router.get(
    "/seguimiento/{codigo}",
    response_model=AtencionSalida,
    responses={status.HTTP_404_NOT_FOUND: {"description": "No hay atención con ese código"}},
)
def consultar_seguimiento(
    codigo: Annotated[str, Path(max_length=16, examples=["CM-4HQ8"])],
    caso_de_uso: Annotated[ConsultarSeguimiento, Depends(obtener_consultar_seguimiento)],
) -> AtencionSalida:
    try:
        atencion = caso_de_uso.ejecutar(codigo)
    except EntidadNoEncontradaError as error:
        raise _error_http(error) from error
    return AtencionSalida.desde_dominio(atencion)
