from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.api.schemas.auth import EntradaEstricta
from app.api.schemas.pedidos import EventoEnvioSalida, ItemPedidoSalida
from app.application.admin import DatosAccesorio, DatosMoto, DatosParametros, DatosTarifaSoat
from app.application.pedidos import VistaPedido
from app.domain.catalogo import TipoMoto
from app.domain.costo_real import ParametrosCosto, TarifaSoat
from app.domain.pagos_envios import Envio, EstadoEnvio, EstadoPago
from app.domain.tienda import CategoriaAccesorio, EstadoPedido


class MotoEntrada(EntradaEstricta):
    marca_id: int = Field(ge=1, examples=[1])
    modelo: str = Field(min_length=1, max_length=80, examples=["CB 190R"])
    anio: int = Field(ge=1990, le=2100, examples=[2026])
    cilindraje_cc: int = Field(ge=1, le=3000, examples=[184])
    tipo: TipoMoto
    precio_cop: int = Field(ge=1, le=1_000_000_000, examples=[10_990_000])
    stock: int = Field(default=0, ge=0, le=100_000)
    consumo_km_galon: float = Field(gt=0, le=500, examples=[120.0])
    costo_mantenimiento_km_cop: int = Field(ge=0, le=100_000, examples=[95])
    descripcion: str = Field(default="", max_length=1000)
    imagen_url: str = Field(default="", max_length=500)

    def a_datos(self) -> DatosMoto:
        return DatosMoto(**self.model_dump())


class AccesorioEntrada(EntradaEstricta):
    sku: str = Field(pattern=r"^[A-Za-z0-9-]{3,30}$", examples=["CAS-010"])
    nombre: str = Field(min_length=2, max_length=120, examples=["Casco modular"])
    categoria: CategoriaAccesorio
    fabricante: str = Field(min_length=1, max_length=80, examples=["Shaft"])
    descripcion: str = Field(default="", max_length=1000)
    precio_cop: int = Field(ge=1, le=1_000_000_000, examples=[489_000])
    stock: int = Field(default=0, ge=0, le=100_000)
    imagen_url: str = Field(default="", max_length=500)

    def a_datos(self) -> DatosAccesorio:
        return DatosAccesorio(**self.model_dump())


class TarifaSoatEntrada(EntradaEstricta):
    cilindraje_min: int = Field(ge=0, examples=[0])
    cilindraje_max: int = Field(ge=0, examples=[99])
    valor_anual_cop: int = Field(ge=1, examples=[256_000])

    @model_validator(mode="after")
    def validar_rango(self) -> "TarifaSoatEntrada":
        if self.cilindraje_min > self.cilindraje_max:
            raise ValueError("cilindraje_min no puede ser mayor que cilindraje_max")
        return self


class ParametrosEntrada(EntradaEstricta):
    precio_galon_cop: int = Field(gt=0, le=1_000_000, examples=[16_200])
    porcentaje_impuesto: float = Field(ge=0, le=100, examples=[1.5])
    tarifas_soat: list[TarifaSoatEntrada] = Field(min_length=1, max_length=20)
    valor_matricula_cop: int | None = Field(default=None, ge=0)
    valor_tramites_cop: int | None = Field(default=None, ge=0)
    tasa_mensual: float | None = Field(default=None, ge=0, lt=1)

    def a_datos(self) -> DatosParametros:
        return DatosParametros(
            precio_galon_cop=self.precio_galon_cop,
            porcentaje_impuesto=self.porcentaje_impuesto,
            tarifas_soat=[DatosTarifaSoat(**t.model_dump()) for t in self.tarifas_soat],
            valor_matricula_cop=self.valor_matricula_cop,
            valor_tramites_cop=self.valor_tramites_cop,
            tasa_mensual=self.tasa_mensual,
        )


class TarifaSoatSalida(BaseModel):
    cilindraje_min: int
    cilindraje_max: int
    valor_anual_cop: int

    @classmethod
    def desde_dominio(cls, tarifa: TarifaSoat) -> "TarifaSoatSalida":
        return cls(
            cilindraje_min=tarifa.cilindraje_min,
            cilindraje_max=tarifa.cilindraje_max,
            valor_anual_cop=tarifa.valor_anual_cop,
        )


class ParametrosSalida(BaseModel):
    precio_galon_cop: int
    porcentaje_impuesto: float
    tarifas_soat: list[TarifaSoatSalida]
    valor_matricula_cop: int
    valor_tramites_cop: int
    tasa_mensual: float

    @classmethod
    def desde_dominio(cls, parametros: ParametrosCosto) -> "ParametrosSalida":
        return cls(
            precio_galon_cop=parametros.precio_galon_cop,
            porcentaje_impuesto=parametros.porcentaje_impuesto,
            tarifas_soat=[TarifaSoatSalida.desde_dominio(t) for t in parametros.tarifas_soat],
            valor_matricula_cop=parametros.valor_matricula_cop,
            valor_tramites_cop=parametros.valor_tramites_cop,
            tasa_mensual=parametros.tasa_mensual,
        )


class EnvioEstadoEntrada(EntradaEstricta):
    estado: EstadoEnvio
    nota: str = Field(default="", max_length=200, examples=["Entregado a la transportadora"])


class EnvioAdminSalida(BaseModel):
    id: int
    numero_guia: str
    estado: EstadoEnvio
    eventos: list[EventoEnvioSalida]

    @classmethod
    def desde_dominio(cls, envio: Envio) -> "EnvioAdminSalida":
        return cls(
            id=envio.id or 0,
            numero_guia=envio.numero_guia,
            estado=envio.estado,
            eventos=[EventoEnvioSalida.desde_dominio(e) for e in envio.eventos],
        )


class PedidoAdminSalida(BaseModel):
    id: int
    cliente_nombre: str
    cliente_correo: str
    estado: EstadoPedido
    estado_pago: EstadoPago | None
    subtotal_cop: int
    costo_envio_cop: int
    total_cop: int
    creado_en: datetime
    items: list[ItemPedidoSalida]
    envio: EnvioAdminSalida | None

    @classmethod
    def desde_vista(cls, vista: VistaPedido) -> "PedidoAdminSalida":
        pedido = vista.pedido
        return cls(
            id=pedido.id or 0,
            cliente_nombre=pedido.usuario.nombre,
            cliente_correo=pedido.usuario.correo,
            estado=pedido.estado,
            estado_pago=vista.pago.estado if vista.pago else None,
            subtotal_cop=pedido.subtotal_cop,
            costo_envio_cop=pedido.costo_envio_cop,
            total_cop=pedido.total_cop(),
            creado_en=pedido.creado_en,
            items=[ItemPedidoSalida.desde_dominio(item) for item in pedido.items],
            envio=EnvioAdminSalida.desde_dominio(vista.envio) if vista.envio else None,
        )
