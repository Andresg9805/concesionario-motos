from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.catalogo import (
    Marca as MarcaDominio,
)
from app.domain.puertos import (
    RepositorioMarcas,
)
from app.infrastructure.models.marca import Marca as MarcaModelo


class RepositorioMarcasSQLAlchemy(RepositorioMarcas):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    @staticmethod
    def _a_dominio(marca: MarcaModelo) -> MarcaDominio:
        return MarcaDominio(
            id=marca.id,
            nombre=marca.nombre,
            color_hex=marca.color_hex,
            descripcion=marca.descripcion or "",
        )

    def listar(self) -> list[MarcaDominio]:
        consulta = select(MarcaModelo).order_by(MarcaModelo.id)
        marcas = self.sesion.scalars(consulta).all()
        return [self._a_dominio(marca) for marca in marcas]

    def buscar_por_id(self, id: int) -> MarcaDominio | None:
        marca = self.sesion.get(MarcaModelo, id)

        if marca is None:
            return None

        return self._a_dominio(marca)
