from pydantic import BaseModel, Field

from app.api.schemas.auth import PATRON_CELULAR, EntradaEstricta
from app.application.tienda import SEPARADOR_DETALLE
from app.domain.tienda import Accesorio, CategoriaAccesorio, Departamento, Direccion, Municipio

PATRON_LINEA = r"^[^\r\n]+$"


class AccesorioSalida(BaseModel):
    id: int
    sku: str
    nombre: str
    categoria: CategoriaAccesorio
    fabricante: str
    descripcion: str
    precio_cop: int
    stock: int
    imagen_url: str

    @classmethod
    def desde_dominio(cls, accesorio: Accesorio) -> "AccesorioSalida":
        return cls(
            id=accesorio.id or 0,
            sku=accesorio.sku,
            nombre=accesorio.nombre,
            categoria=accesorio.categoria,
            fabricante=accesorio.fabricante,
            descripcion=accesorio.descripcion,
            precio_cop=accesorio.precio_cop,
            stock=accesorio.stock,
            imagen_url=accesorio.imagen_url,
        )


class DepartamentoSalida(BaseModel):
    codigo: str
    nombre: str
    costo_envio_cop: int
    dias_envio: int

    @classmethod
    def desde_dominio(cls, departamento: Departamento) -> "DepartamentoSalida":
        return cls(
            codigo=departamento.codigo,
            nombre=departamento.nombre,
            costo_envio_cop=departamento.costo_envio_cop,
            dias_envio=departamento.dias_envio,
        )


class MunicipioSalida(BaseModel):
    codigo: str
    nombre: str

    @classmethod
    def desde_dominio(cls, municipio: Municipio) -> "MunicipioSalida":
        return cls(codigo=municipio.codigo, nombre=municipio.nombre)


class TarifaEnvioSalida(BaseModel):
    departamento: str
    costo_envio_cop: int
    dias_envio: int

    @classmethod
    def desde_dominio(cls, departamento: Departamento) -> "TarifaEnvioSalida":
        return cls(
            departamento=departamento.codigo,
            costo_envio_cop=departamento.costo_envio_cop,
            dias_envio=departamento.dias_envio,
        )


class DireccionEntrada(EntradaEstricta):
    nombre_recibe: str = Field(min_length=3, max_length=120, examples=["Ana Pérez"])
    telefono: str = Field(pattern=PATRON_CELULAR, examples=["3001234567"])
    departamento_codigo: str = Field(pattern=r"^\d{2}$", examples=["11"])
    municipio_codigo: str = Field(pattern=r"^\d{5}$", examples=["11001"])
    municipio_nombre: str = Field(min_length=1, max_length=120, examples=["Bogotá D.C."])
    direccion: str = Field(
        min_length=5, max_length=200, pattern=PATRON_LINEA, examples=["Calle 26 # 13-19"]
    )
    detalle: str = Field(default="", max_length=120, pattern=r"^[^\r\n]*$", examples=["Apto 302"])


class DireccionSalida(BaseModel):
    id: int
    nombre_recibe: str
    telefono: str
    departamento_codigo: str
    municipio_codigo: str
    municipio_nombre: str
    direccion: str
    detalle: str

    @classmethod
    def desde_dominio(cls, direccion: Direccion) -> "DireccionSalida":
        calle, _, complemento = direccion.detalle.partition(SEPARADOR_DETALLE)
        return cls(
            id=direccion.id or 0,
            nombre_recibe=direccion.nombre_recibe,
            telefono=direccion.telefono_contacto,
            departamento_codigo=direccion.municipio.departamento.codigo,
            municipio_codigo=direccion.municipio.codigo,
            municipio_nombre=direccion.municipio.nombre,
            direccion=calle,
            detalle=complemento,
        )
