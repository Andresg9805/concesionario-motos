from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.catalogo import (
    CategoriaLicencia,
    TipoMoto,
)
from app.domain.catalogo import (
    Marca as MarcaDominio,
)
from app.domain.catalogo import (
    Moto as MotoDominio,
)
from app.domain.puertos import (
    FiltrosMoto,
    RepositorioMotos,
)
from app.infrastructure.models.marca import Marca as MarcaModelo
from app.infrastructure.models.moto import Moto as MotoModelo


class RepositorioMotosSQLAlchemy(RepositorioMotos):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    @staticmethod
    def _a_dominio(moto: MotoModelo) -> MotoDominio:
        marca = MarcaDominio(
            id=moto.marca.id,
            nombre=moto.marca.nombre,
            color_hex=moto.marca.color_hex,
            descripcion=moto.marca.descripcion or "",
        )

        return MotoDominio(
            id=moto.id,
            marca=marca,
            modelo=moto.modelo,
            anio=moto.anio,
            cilindraje_cc=moto.cilindraje_cc,
            tipo=TipoMoto(moto.tipo),
            categoria_licencia=CategoriaLicencia(moto.categoria_licencia),
            precio_cop=moto.precio_cop,
            stock=moto.stock,
            consumo_km_galon=moto.consumo_km_galon,
            costo_mantenimiento_km_cop=moto.costo_mantenimiento_km_cop,
            descripcion=moto.descripcion or "",
            imagen_url=moto.imagen_url or "",
        )

    def listar(self, filtros: FiltrosMoto) -> list[MotoDominio]:
        consulta = select(MotoModelo)

        if filtros.marca_id is not None:
            consulta = consulta.where(
                MotoModelo.marca_id == filtros.marca_id
            )

        if filtros.tipo is not None:
            consulta = consulta.where(
                MotoModelo.tipo == filtros.tipo.value
            )

        if filtros.categoria_licencia is not None:
            consulta = consulta.where(
                MotoModelo.categoria_licencia
                == filtros.categoria_licencia.value
            )

        if filtros.precio_min is not None:
            consulta = consulta.where(
                MotoModelo.precio_cop >= filtros.precio_min
            )

        if filtros.precio_max is not None:
            consulta = consulta.where(
                MotoModelo.precio_cop <= filtros.precio_max
            )

        if filtros.cilindraje_min is not None:
            consulta = consulta.where(
                MotoModelo.cilindraje_cc >= filtros.cilindraje_min
            )

        if filtros.cilindraje_max is not None:
            consulta = consulta.where(
                MotoModelo.cilindraje_cc <= filtros.cilindraje_max
            )

        consulta = consulta.order_by(MotoModelo.id)

        motos = self.sesion.scalars(consulta).all()
        return [self._a_dominio(moto) for moto in motos]

    def buscar_por_id(self, id: int) -> MotoDominio | None:
        moto = self.sesion.get(MotoModelo, id)

        if moto is None:
            return None

        return self._a_dominio(moto)

    def guardar(self, moto: MotoDominio) -> MotoDominio:
        if moto.marca.id is None:
            raise ValueError("La marca debe estar registrada en la base de datos")

        marca = self.sesion.get(MarcaModelo, moto.marca.id)

        if marca is None:
            raise ValueError("La marca indicada no existe en la base de datos")

        modelo = (
            self.sesion.get(MotoModelo, moto.id)
            if moto.id is not None
            else None
        )

        if modelo is None:
            if moto.id is not None:
                raise ValueError("La moto indicada no existe en la base de datos")

            modelo = MotoModelo()
            self.sesion.add(modelo)

        modelo.marca_id = marca.id
        modelo.modelo = moto.modelo
        modelo.anio = moto.anio
        modelo.cilindraje_cc = moto.cilindraje_cc
        modelo.tipo = moto.tipo.value
        modelo.categoria_licencia = moto.categoria_licencia.value
        modelo.precio_cop = moto.precio_cop
        modelo.stock = moto.stock
        modelo.consumo_km_galon = moto.consumo_km_galon
        modelo.costo_mantenimiento_km_cop = moto.costo_mantenimiento_km_cop
        modelo.descripcion = moto.descripcion
        modelo.imagen_url = moto.imagen_url

        self.sesion.flush()

        return self._a_dominio(modelo)

    def eliminar(self, id: int) -> None:
        moto = self.sesion.get(MotoModelo, id)

        if moto is not None:
            self.sesion.delete(moto)
            self.sesion.flush()
