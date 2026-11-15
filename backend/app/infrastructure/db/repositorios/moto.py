from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.catalogo import Moto
from app.domain.puertos import FiltrosMoto, RepositorioMotos
from app.infrastructure.db.repositorios.conversiones import moto_a_dominio, rango_cilindraje
from app.infrastructure.models.marca import Marca as MarcaModelo
from app.infrastructure.models.moto import Moto as MotoModelo
from app.infrastructure.models.tipo_moto import TipoMoto as TipoMotoModelo


class RepositorioMotosSQLAlchemy(RepositorioMotos):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar(self, filtros: FiltrosMoto) -> list[Moto]:
        consulta = select(MotoModelo).join(MotoModelo.tipo)

        if filtros.marca_id is not None:
            consulta = consulta.where(MotoModelo.marca_id == filtros.marca_id)
        if filtros.tipo is not None:
            consulta = consulta.where(TipoMotoModelo.clave == filtros.tipo.value)
        if filtros.categoria_licencia is not None:
            minimo, maximo = rango_cilindraje(filtros.categoria_licencia)
            consulta = consulta.where(MotoModelo.cilindraje_cc >= minimo)
            if maximo is not None:
                consulta = consulta.where(MotoModelo.cilindraje_cc <= maximo)
        if filtros.precio_min is not None:
            consulta = consulta.where(MotoModelo.precio_cop >= filtros.precio_min)
        if filtros.precio_max is not None:
            consulta = consulta.where(MotoModelo.precio_cop <= filtros.precio_max)
        if filtros.cilindraje_min is not None:
            consulta = consulta.where(MotoModelo.cilindraje_cc >= filtros.cilindraje_min)
        if filtros.cilindraje_max is not None:
            consulta = consulta.where(MotoModelo.cilindraje_cc <= filtros.cilindraje_max)

        motos = self.sesion.scalars(consulta.order_by(MotoModelo.id)).all()
        return [moto_a_dominio(moto) for moto in motos]

    def buscar_por_id(self, id: int) -> Moto | None:
        moto = self.sesion.get(MotoModelo, id)
        return None if moto is None else moto_a_dominio(moto)

    def guardar(self, moto: Moto) -> Moto:
        if moto.marca.id is None or self.sesion.get(MarcaModelo, moto.marca.id) is None:
            raise ValueError("La marca indicada no existe en la base de datos")

        tipo = self.sesion.scalar(
            select(TipoMotoModelo).where(TipoMotoModelo.clave == moto.tipo.value)
        )
        if tipo is None:
            raise ValueError("El tipo de moto no existe en la base de datos")

        if moto.id is None:
            modelo = MotoModelo()
            self.sesion.add(modelo)
        else:
            existente = self.sesion.get(MotoModelo, moto.id)
            if existente is None:
                raise ValueError("La moto indicada no existe en la base de datos")
            modelo = existente

        modelo.marca_id = moto.marca.id
        modelo.tipo_id = tipo.id
        modelo.modelo = moto.modelo
        modelo.anio = moto.anio
        modelo.cilindraje_cc = moto.cilindraje_cc
        modelo.precio_cop = moto.precio_cop
        modelo.stock = moto.stock
        modelo.consumo_km_galon = moto.consumo_km_galon
        modelo.costo_mantenimiento_km_cop = moto.costo_mantenimiento_km_cop
        modelo.descripcion = moto.descripcion
        modelo.imagen_url = moto.imagen_url

        self.sesion.flush()
        self.sesion.refresh(modelo)
        return moto_a_dominio(modelo)

    def eliminar(self, id: int) -> None:
        moto = self.sesion.get(MotoModelo, id)
        if moto is not None:
            self.sesion.delete(moto)
            self.sesion.flush()
