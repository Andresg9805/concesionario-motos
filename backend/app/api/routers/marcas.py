from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencias import obtener_listar_marcas
from app.api.schemas.motos import MarcaSalida
from app.application.motos import ListarMarcas

router = APIRouter(prefix="/marcas", tags=["Catálogo"])


@router.get("", response_model=list[MarcaSalida])
def listar_marcas(
    caso_de_uso: Annotated[ListarMarcas, Depends(obtener_listar_marcas)],
) -> list[MarcaSalida]:
    return [MarcaSalida.desde_dominio(marca) for marca in caso_de_uso.ejecutar()]
