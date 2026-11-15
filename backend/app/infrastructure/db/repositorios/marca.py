from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.catalogo import Marca
from app.domain.puertos import RepositorioMarcas
from app.infrastructure.db.repositorios.conversiones import marca_a_dominio
from app.infrastructure.models.marca import Marca as MarcaModelo


class RepositorioMarcasSQLAlchemy(RepositorioMarcas):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar(self) -> list[Marca]:
        marcas = self.sesion.scalars(select(MarcaModelo).order_by(MarcaModelo.id)).all()
        return [marca_a_dominio(marca) for marca in marcas]

    def buscar_por_id(self, id: int) -> Marca | None:
        marca = self.sesion.get(MarcaModelo, id)
        return None if marca is None else marca_a_dominio(marca)
