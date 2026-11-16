from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.puertos import (
    RepositorioAccesorios,
    RepositorioDirecciones,
    RepositorioUbicaciones,
)
from app.domain.tienda import Accesorio, CategoriaAccesorio, Departamento, Direccion, Municipio
from app.infrastructure.db.repositorios.conversiones import (
    accesorio_a_dominio,
    departamento_a_dominio,
    direccion_a_dominio,
    municipio_a_dominio,
)
from app.infrastructure.models.accesorio import Accesorio as AccesorioModelo
from app.infrastructure.models.categoria_accesorio import (
    CategoriaAccesorio as CategoriaAccesorioModelo,
)
from app.infrastructure.models.departamento import Departamento as DepartamentoModelo
from app.infrastructure.models.direccion import Direccion as DireccionModelo
from app.infrastructure.models.fabricante import Fabricante as FabricanteModelo
from app.infrastructure.models.municipio import Municipio as MunicipioModelo
from app.infrastructure.models.usuario import Usuario as UsuarioModelo


class RepositorioAccesoriosSQLAlchemy(RepositorioAccesorios):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar(self, categoria: CategoriaAccesorio | None = None) -> list[Accesorio]:
        consulta = select(AccesorioModelo).join(AccesorioModelo.categoria)
        if categoria is not None:
            consulta = consulta.where(CategoriaAccesorioModelo.clave == categoria.value)
        accesorios = self.sesion.scalars(consulta.order_by(AccesorioModelo.id)).all()
        return [accesorio_a_dominio(accesorio) for accesorio in accesorios]

    def buscar_por_id(self, id: int) -> Accesorio | None:
        accesorio = self.sesion.get(AccesorioModelo, id)
        return None if accesorio is None else accesorio_a_dominio(accesorio)

    def guardar(self, accesorio: Accesorio) -> Accesorio:
        categoria = self.sesion.scalar(
            select(CategoriaAccesorioModelo).where(
                CategoriaAccesorioModelo.clave == accesorio.categoria.value
            )
        )
        if categoria is None:
            raise ValueError("La categoría no existe en la base de datos")

        fabricante = self.sesion.scalar(
            select(FabricanteModelo).where(FabricanteModelo.nombre == accesorio.fabricante)
        )
        if fabricante is None:
            fabricante = FabricanteModelo(nombre=accesorio.fabricante)
            self.sesion.add(fabricante)

        if accesorio.id is None:
            modelo = AccesorioModelo()
            self.sesion.add(modelo)
        else:
            existente = self.sesion.get(AccesorioModelo, accesorio.id)
            if existente is None:
                raise ValueError("El accesorio indicado no existe en la base de datos")
            modelo = existente

        modelo.sku = accesorio.sku
        modelo.nombre = accesorio.nombre
        modelo.categoria = categoria
        modelo.fabricante = fabricante
        modelo.descripcion = accesorio.descripcion
        modelo.precio_cop = accesorio.precio_cop
        modelo.stock = accesorio.stock
        modelo.imagen_url = accesorio.imagen_url

        self.sesion.flush()
        accesorio.id = modelo.id
        return accesorio_a_dominio(modelo)

    def eliminar(self, id: int) -> None:
        accesorio = self.sesion.get(AccesorioModelo, id)
        if accesorio is not None:
            self.sesion.delete(accesorio)
            self.sesion.flush()


class RepositorioUbicacionesSQLAlchemy(RepositorioUbicaciones):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar_departamentos(self) -> list[Departamento]:
        departamentos = self.sesion.scalars(
            select(DepartamentoModelo).order_by(DepartamentoModelo.nombre)
        ).all()
        return [departamento_a_dominio(departamento) for departamento in departamentos]

    def listar_municipios(self, departamento_codigo: str) -> list[Municipio]:
        municipios = self.sesion.scalars(
            select(MunicipioModelo)
            .where(MunicipioModelo.departamento_codigo == departamento_codigo)
            .order_by(MunicipioModelo.nombre)
        ).all()
        return [municipio_a_dominio(municipio) for municipio in municipios]

    def buscar_municipio(self, codigo: str) -> Municipio | None:
        municipio = self.sesion.get(MunicipioModelo, codigo)
        return None if municipio is None else municipio_a_dominio(municipio)


class RepositorioDireccionesSQLAlchemy(RepositorioDirecciones):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, direccion: Direccion) -> Direccion:
        if self.sesion.get(UsuarioModelo, direccion.usuario.id or 0) is None:
            raise ValueError("El usuario indicado no existe en la base de datos")
        if self.sesion.get(MunicipioModelo, direccion.municipio.codigo) is None:
            raise ValueError("El municipio indicado no existe en la base de datos")

        if direccion.id is None:
            modelo = DireccionModelo()
            self.sesion.add(modelo)
        else:
            existente = self.sesion.get(DireccionModelo, direccion.id)
            if existente is None:
                raise ValueError("La dirección indicada no existe en la base de datos")
            modelo = existente

        modelo.usuario_id = direccion.usuario.id or 0
        modelo.municipio_codigo = direccion.municipio.codigo
        modelo.detalle = direccion.detalle
        modelo.telefono_contacto = direccion.telefono_contacto
        modelo.nombre_recibe = direccion.nombre_recibe

        self.sesion.flush()
        self.sesion.refresh(modelo)
        direccion.id = modelo.id
        return direccion_a_dominio(modelo)

    def buscar_por_id(self, id: int) -> Direccion | None:
        direccion = self.sesion.get(DireccionModelo, id)
        return None if direccion is None else direccion_a_dominio(direccion)

    def listar_por_usuario(self, usuario_id: int) -> list[Direccion]:
        direcciones = self.sesion.scalars(
            select(DireccionModelo)
            .where(DireccionModelo.usuario_id == usuario_id)
            .order_by(DireccionModelo.id)
        ).all()
        return [direccion_a_dominio(direccion) for direccion in direcciones]
