from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from app.api.dependencias import (
    obtener_actualizar_accesorio,
    obtener_actualizar_moto,
    obtener_actualizar_parametros,
    obtener_avanzar_envio,
    obtener_crear_accesorio,
    obtener_crear_moto,
    obtener_eliminar_accesorio,
    obtener_eliminar_moto,
    obtener_listar_pedidos_admin,
    obtener_obtener_parametros,
    requerir_rol,
)
from app.api.schemas.admin import (
    AccesorioEntrada,
    EnvioAdminSalida,
    EnvioEstadoEntrada,
    MotoEntrada,
    ParametrosEntrada,
    ParametrosSalida,
    PedidoAdminSalida,
)
from app.api.schemas.motos import MotoDetalleSalida
from app.api.schemas.tienda import AccesorioSalida
from app.application.admin import (
    ActualizarAccesorio,
    ActualizarMoto,
    ActualizarParametros,
    AvanzarEnvio,
    CrearAccesorio,
    CrearMoto,
    EliminarAccesorio,
    EliminarMoto,
    ListarPedidosAdmin,
    ObtenerParametros,
)
from app.domain.atencion import Rol
from app.domain.excepciones import EntidadNoEncontradaError, TransicionInvalidaError

router = APIRouter(tags=["Administración"], dependencies=[Depends(requerir_rol(Rol.ADMIN))])

RESPUESTAS_ADMIN: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"description": "No autenticado"},
    status.HTTP_403_FORBIDDEN: {"description": "Solo el administrador puede hacerlo"},
}

RESPUESTAS_RECURSO: dict[int | str, dict[str, Any]] = {
    **RESPUESTAS_ADMIN,
    status.HTTP_404_NOT_FOUND: {"description": "El recurso o la marca no existe"},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Datos inválidos"},
}

IdPath = Annotated[int, Path(ge=1)]


def no_encontrado(error: EntidadNoEncontradaError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.mensaje)


def invalido(error: ValueError | TransicionInvalidaError) -> HTTPException:
    detalle = error.mensaje if isinstance(error, TransicionInvalidaError) else str(error)
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detalle)


@router.post(
    "/admin/motos",
    status_code=status.HTTP_201_CREATED,
    response_model=MotoDetalleSalida,
    responses=RESPUESTAS_RECURSO,
)
def crear_moto(
    entrada: MotoEntrada,
    caso_de_uso: Annotated[CrearMoto, Depends(obtener_crear_moto)],
) -> MotoDetalleSalida:
    try:
        moto = caso_de_uso.ejecutar(entrada.a_datos())
    except EntidadNoEncontradaError as error:
        raise no_encontrado(error) from error
    except ValueError as error:
        raise invalido(error) from error
    return MotoDetalleSalida.desde_dominio(moto)


@router.put(
    "/admin/motos/{moto_id}", response_model=MotoDetalleSalida, responses=RESPUESTAS_RECURSO
)
def actualizar_moto(
    moto_id: IdPath,
    entrada: MotoEntrada,
    caso_de_uso: Annotated[ActualizarMoto, Depends(obtener_actualizar_moto)],
) -> MotoDetalleSalida:
    try:
        moto = caso_de_uso.ejecutar(moto_id, entrada.a_datos())
    except EntidadNoEncontradaError as error:
        raise no_encontrado(error) from error
    except ValueError as error:
        raise invalido(error) from error
    return MotoDetalleSalida.desde_dominio(moto)


@router.delete(
    "/admin/motos/{moto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPUESTAS_RECURSO,
)
def eliminar_moto(
    moto_id: IdPath,
    caso_de_uso: Annotated[EliminarMoto, Depends(obtener_eliminar_moto)],
) -> Response:
    try:
        caso_de_uso.ejecutar(moto_id)
    except EntidadNoEncontradaError as error:
        raise no_encontrado(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/admin/accesorios",
    status_code=status.HTTP_201_CREATED,
    response_model=AccesorioSalida,
    responses=RESPUESTAS_RECURSO,
)
def crear_accesorio(
    entrada: AccesorioEntrada,
    caso_de_uso: Annotated[CrearAccesorio, Depends(obtener_crear_accesorio)],
) -> AccesorioSalida:
    try:
        accesorio = caso_de_uso.ejecutar(entrada.a_datos())
    except ValueError as error:
        raise invalido(error) from error
    return AccesorioSalida.desde_dominio(accesorio)


@router.put(
    "/admin/accesorios/{accesorio_id}",
    response_model=AccesorioSalida,
    responses=RESPUESTAS_RECURSO,
)
def actualizar_accesorio(
    accesorio_id: IdPath,
    entrada: AccesorioEntrada,
    caso_de_uso: Annotated[ActualizarAccesorio, Depends(obtener_actualizar_accesorio)],
) -> AccesorioSalida:
    try:
        accesorio = caso_de_uso.ejecutar(accesorio_id, entrada.a_datos())
    except EntidadNoEncontradaError as error:
        raise no_encontrado(error) from error
    except ValueError as error:
        raise invalido(error) from error
    return AccesorioSalida.desde_dominio(accesorio)


@router.delete(
    "/admin/accesorios/{accesorio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPUESTAS_RECURSO,
)
def eliminar_accesorio(
    accesorio_id: IdPath,
    caso_de_uso: Annotated[EliminarAccesorio, Depends(obtener_eliminar_accesorio)],
) -> Response:
    try:
        caso_de_uso.ejecutar(accesorio_id)
    except EntidadNoEncontradaError as error:
        raise no_encontrado(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/parametros-costo", response_model=ParametrosSalida, responses=RESPUESTAS_ADMIN)
def obtener_parametros(
    caso_de_uso: Annotated[ObtenerParametros, Depends(obtener_obtener_parametros)],
) -> ParametrosSalida:
    return ParametrosSalida.desde_dominio(caso_de_uso.ejecutar())


@router.put("/parametros-costo", response_model=ParametrosSalida, responses=RESPUESTAS_RECURSO)
def actualizar_parametros(
    entrada: ParametrosEntrada,
    caso_de_uso: Annotated[ActualizarParametros, Depends(obtener_actualizar_parametros)],
) -> ParametrosSalida:
    try:
        parametros = caso_de_uso.ejecutar(entrada.a_datos())
    except ValueError as error:
        raise invalido(error) from error
    return ParametrosSalida.desde_dominio(parametros)


@router.get("/admin/pedidos", response_model=list[PedidoAdminSalida], responses=RESPUESTAS_ADMIN)
def listar_pedidos(
    caso_de_uso: Annotated[ListarPedidosAdmin, Depends(obtener_listar_pedidos_admin)],
) -> list[PedidoAdminSalida]:
    return [PedidoAdminSalida.desde_vista(vista) for vista in caso_de_uso.ejecutar()]


@router.patch(
    "/envios/{envio_id}/estado", response_model=EnvioAdminSalida, responses=RESPUESTAS_RECURSO
)
def cambiar_estado_envio(
    envio_id: IdPath,
    entrada: EnvioEstadoEntrada,
    caso_de_uso: Annotated[AvanzarEnvio, Depends(obtener_avanzar_envio)],
) -> EnvioAdminSalida:
    try:
        envio = caso_de_uso.ejecutar(envio_id, entrada.estado, entrada.nota)
    except EntidadNoEncontradaError as error:
        raise no_encontrado(error) from error
    except TransicionInvalidaError as error:
        raise invalido(error) from error
    return EnvioAdminSalida.desde_dominio(envio)


@router.get("/reportes/demanda", responses=RESPUESTAS_ADMIN)
def reporte_demanda() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="El radar de demanda con DuckDB aún no está integrado",
    )


@router.get("/reportes/ventas", responses=RESPUESTAS_ADMIN)
def reporte_ventas() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="El reporte de ventas con DuckDB aún no está integrado",
    )
