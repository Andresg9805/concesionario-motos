from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.api.dependencias import (
    obtener_crear_direccion,
    obtener_listar_direcciones_propias,
    obtener_obtener_direccion_propia,
    requerir_rol,
)
from app.api.schemas.tienda import DireccionEntrada, DireccionSalida
from app.application.tienda import (
    CrearDireccion,
    DatosDireccion,
    ListarDireccionesPropias,
    ObtenerDireccionPropia,
)
from app.domain.atencion import Rol
from app.domain.excepciones import DireccionInvalidaError, EntidadNoEncontradaError
from app.domain.seguridad import DatosToken

router = APIRouter(prefix="/mis-direcciones", tags=["Direcciones"])

SesionCliente = Annotated[DatosToken, Depends(requerir_rol(Rol.CLIENTE))]

RESPUESTAS_PROTEGIDAS: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"description": "No autenticado"},
    status.HTTP_403_FORBIDDEN: {"description": "Solo los clientes tienen direcciones"},
}


@router.get("", response_model=list[DireccionSalida], responses=RESPUESTAS_PROTEGIDAS)
def listar_mis_direcciones(
    sesion: SesionCliente,
    caso_de_uso: Annotated[ListarDireccionesPropias, Depends(obtener_listar_direcciones_propias)],
) -> list[DireccionSalida]:
    return [
        DireccionSalida.desde_dominio(direccion)
        for direccion in caso_de_uso.ejecutar(sesion.usuario_id)
    ]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DireccionSalida,
    responses={
        **RESPUESTAS_PROTEGIDAS,
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Datos o municipio no válidos"},
    },
)
def crear_direccion(
    entrada: DireccionEntrada,
    sesion: SesionCliente,
    caso_de_uso: Annotated[CrearDireccion, Depends(obtener_crear_direccion)],
) -> DireccionSalida:
    try:
        direccion = caso_de_uso.ejecutar(
            sesion.usuario_id,
            DatosDireccion(
                nombre_recibe=entrada.nombre_recibe,
                telefono=entrada.telefono,
                departamento_codigo=entrada.departamento_codigo,
                municipio_codigo=entrada.municipio_codigo,
                direccion=entrada.direccion,
                detalle=entrada.detalle,
            ),
        )
    except DireccionInvalidaError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=error.mensaje
        ) from error
    except EntidadNoEncontradaError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.mensaje) from error
    return DireccionSalida.desde_dominio(direccion)


@router.get(
    "/{direccion_id}",
    response_model=DireccionSalida,
    responses={
        **RESPUESTAS_PROTEGIDAS,
        status.HTTP_404_NOT_FOUND: {"description": "La dirección no existe o es de otro cliente"},
    },
)
def obtener_direccion(
    direccion_id: Annotated[int, Path(ge=1)],
    sesion: SesionCliente,
    caso_de_uso: Annotated[ObtenerDireccionPropia, Depends(obtener_obtener_direccion_propia)],
) -> DireccionSalida:
    try:
        direccion = caso_de_uso.ejecutar(sesion.usuario_id, direccion_id)
    except EntidadNoEncontradaError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.mensaje) from error
    return DireccionSalida.desde_dominio(direccion)
