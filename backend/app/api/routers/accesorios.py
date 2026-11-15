from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.dependencias import obtener_listar_accesorios, obtener_obtener_accesorio
from app.api.schemas.tienda import AccesorioSalida
from app.application.tienda import ListarAccesorios, ObtenerAccesorio
from app.domain.excepciones import EntidadNoEncontradaError
from app.domain.tienda import CategoriaAccesorio

router = APIRouter(prefix="/accesorios", tags=["Tienda"])

RESPUESTA_404: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {"description": "El accesorio no existe"}
}


@router.get("", response_model=list[AccesorioSalida])
def listar_accesorios(
    caso_de_uso: Annotated[ListarAccesorios, Depends(obtener_listar_accesorios)],
    categoria: Annotated[CategoriaAccesorio | None, Query()] = None,
) -> list[AccesorioSalida]:
    return [
        AccesorioSalida.desde_dominio(accesorio) for accesorio in caso_de_uso.ejecutar(categoria)
    ]


@router.get("/{accesorio_id}", response_model=AccesorioSalida, responses=RESPUESTA_404)
def obtener_accesorio(
    accesorio_id: Annotated[int, Path(ge=1)],
    caso_de_uso: Annotated[ObtenerAccesorio, Depends(obtener_obtener_accesorio)],
) -> AccesorioSalida:
    try:
        accesorio = caso_de_uso.ejecutar(accesorio_id)
    except EntidadNoEncontradaError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=error.mensaje) from error
    return AccesorioSalida.desde_dominio(accesorio)
