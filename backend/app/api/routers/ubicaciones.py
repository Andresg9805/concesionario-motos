from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.dependencias import (
    obtener_listar_departamentos,
    obtener_listar_municipios,
    obtener_obtener_departamento,
)
from app.api.schemas.tienda import DepartamentoSalida, MunicipioSalida, TarifaEnvioSalida
from app.application.tienda import ListarDepartamentos, ListarMunicipios, ObtenerDepartamento
from app.domain.excepciones import EntidadNoEncontradaError

router = APIRouter(tags=["Tienda"])

RESPUESTA_404: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {"description": "El departamento no existe"}
}


def _no_encontrado(error: EntidadNoEncontradaError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.mensaje)


@router.get("/departamentos", response_model=list[DepartamentoSalida])
def listar_departamentos(
    caso_de_uso: Annotated[ListarDepartamentos, Depends(obtener_listar_departamentos)],
) -> list[DepartamentoSalida]:
    return [DepartamentoSalida.desde_dominio(d) for d in caso_de_uso.ejecutar()]


@router.get(
    "/departamentos/{codigo}/municipios",
    response_model=list[MunicipioSalida],
    responses=RESPUESTA_404,
)
def listar_municipios(
    codigo: Annotated[str, Path(max_length=5, examples=["11"])],
    caso_de_uso: Annotated[ListarMunicipios, Depends(obtener_listar_municipios)],
) -> list[MunicipioSalida]:
    try:
        municipios = caso_de_uso.ejecutar(codigo)
    except EntidadNoEncontradaError as error:
        raise _no_encontrado(error) from error
    return [MunicipioSalida.desde_dominio(m) for m in municipios]


@router.get("/envios/tarifa", response_model=TarifaEnvioSalida, responses=RESPUESTA_404)
def consultar_tarifa_envio(
    departamento: Annotated[str, Query(max_length=5, examples=["11"])],
    caso_de_uso: Annotated[ObtenerDepartamento, Depends(obtener_obtener_departamento)],
) -> TarifaEnvioSalida:
    try:
        resultado = caso_de_uso.ejecutar(departamento)
    except EntidadNoEncontradaError as error:
        raise _no_encontrado(error) from error
    return TarifaEnvioSalida.desde_dominio(resultado)
