from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.api.dependencias import (
    obtener_atender_siguiente_test_drive,
    obtener_cambiar_estado_cotizacion,
    obtener_listar_atenciones_asesor,
    obtener_listar_cola_test_drives,
    requerir_rol,
)
from app.api.schemas.atencion import (
    AtencionAsesorSalida,
    CambioEstadoEntrada,
    ProgramarTestDriveEntrada,
)
from app.application.atencion import (
    AtenderSiguienteTestDrive,
    CambiarEstadoCotizacion,
    ListarAtencionesAsesor,
    ListarColaTestDrives,
)
from app.domain.atencion import Rol
from app.domain.excepciones import (
    EntidadNoEncontradaError,
    PermisoDenegadoError,
    TestDriveInvalidoError,
    TransicionInvalidaError,
)
from app.domain.seguridad import DatosToken

router = APIRouter(tags=["Panel del asesor"])

SesionAsesor = Annotated[DatosToken, Depends(requerir_rol(Rol.ASESOR))]


@router.get("/asesor/atenciones", response_model=list[AtencionAsesorSalida])
def listar_atenciones(
    sesion: SesionAsesor,
    caso_de_uso: Annotated[ListarAtencionesAsesor, Depends(obtener_listar_atenciones_asesor)],
) -> list[AtencionAsesorSalida]:
    return [
        AtencionAsesorSalida.desde_dominio(cotizacion)
        for cotizacion in caso_de_uso.ejecutar(sesion.usuario_id)
    ]


@router.patch(
    "/cotizaciones/{cotizacion_id}/estado",
    response_model=AtencionAsesorSalida,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "La cotización es de otro asesor"},
        status.HTTP_404_NOT_FOUND: {"description": "La cotización no existe"},
        status.HTTP_409_CONFLICT: {"description": "La transición de estado no es válida"},
    },
)
def cambiar_estado(
    cotizacion_id: Annotated[int, Path(ge=1)],
    entrada: CambioEstadoEntrada,
    sesion: SesionAsesor,
    caso_de_uso: Annotated[CambiarEstadoCotizacion, Depends(obtener_cambiar_estado_cotizacion)],
) -> AtencionAsesorSalida:
    try:
        cotizacion = caso_de_uso.ejecutar(sesion.usuario_id, cotizacion_id, entrada.estado)
    except EntidadNoEncontradaError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.mensaje) from error
    except PermisoDenegadoError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error.mensaje) from error
    except TransicionInvalidaError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error.mensaje) from error
    return AtencionAsesorSalida.desde_dominio(cotizacion)


@router.get("/asesor/test-drives", response_model=list[AtencionAsesorSalida])
def listar_cola_test_drives(
    sesion: SesionAsesor,
    caso_de_uso: Annotated[ListarColaTestDrives, Depends(obtener_listar_cola_test_drives)],
) -> list[AtencionAsesorSalida]:
    return [
        AtencionAsesorSalida.desde_dominio(test_drive)
        for test_drive in caso_de_uso.ejecutar(sesion.usuario_id)
    ]


@router.post(
    "/asesor/test-drives/siguiente",
    response_model=AtencionAsesorSalida,
    responses={status.HTTP_404_NOT_FOUND: {"description": "La cola está vacía"}},
)
def atender_siguiente_test_drive(
    entrada: ProgramarTestDriveEntrada,
    sesion: SesionAsesor,
    caso_de_uso: Annotated[
        AtenderSiguienteTestDrive, Depends(obtener_atender_siguiente_test_drive)
    ],
) -> AtencionAsesorSalida:
    try:
        test_drive = caso_de_uso.ejecutar(sesion.usuario_id, entrada.fecha)
    except EntidadNoEncontradaError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.mensaje) from error
    except TestDriveInvalidoError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=error.mensaje
        ) from error
    return AtencionAsesorSalida.desde_dominio(test_drive)
