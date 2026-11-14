from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum

from app.domain.atencion import Usuario
from app.domain.catalogo import Moto
from app.domain.excepciones import (
    PedidoInvalidoError,
    StockInsuficienteError,
    TransicionInvalidaError,
)

MINUTOS_RESERVA = 15


class CategoriaAccesorio(StrEnum):
    CASCO = "CASCO"
    CHAQUETA = "CHAQUETA"
    GUANTES = "GUANTES"
    RODILLERA = "RODILLERA"
    HOMBRERA = "HOMBRERA"
    MALETA = "MALETA"
    MANTENIMIENTO = "MANTENIMIENTO"


class EstadoPedido(StrEnum):
    PENDIENTE_PAGO = "PENDIENTE_PAGO"
    PAGADO = "PAGADO"
    EXPIRADO = "EXPIRADO"


@dataclass(kw_only=True)
class Accesorio:
    id: int | None = None
    sku: str
    nombre: str
    categoria: CategoriaAccesorio
    descripcion: str = ""
    precio_cop: int
    stock: int = 0
    imagen_url: str = ""
    motos_compatibles: list[Moto] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.precio_cop <= 0:
            raise ValueError("El precio debe ser mayor que cero")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")

    def hay_stock(self, cantidad: int) -> bool:
        return self.stock >= cantidad

    def reservar(self, cantidad: int) -> None:
        if cantidad <= 0:
            raise PedidoInvalidoError("La cantidad debe ser mayor que cero")
        if not self.hay_stock(cantidad):
            raise StockInsuficienteError(f"Solo hay {self.stock} unidades de {self.nombre}")
        self.stock -= cantidad

    def liberar(self, cantidad: int) -> None:
        if cantidad <= 0:
            raise PedidoInvalidoError("La cantidad debe ser mayor que cero")
        self.stock += cantidad


@dataclass(kw_only=True)
class Departamento:
    codigo: str
    nombre: str
    costo_envio_cop: int
    dias_envio: int

    def __post_init__(self) -> None:
        if self.costo_envio_cop < 0 or self.dias_envio <= 0:
            raise ValueError("El costo y los días de envío no son válidos")


@dataclass(kw_only=True)
class Municipio:
    codigo: str
    nombre: str
    departamento: Departamento


@dataclass(kw_only=True)
class Direccion:
    id: int | None = None
    usuario: Usuario
    municipio: Municipio
    detalle: str
    telefono_contacto: str

    def __post_init__(self) -> None:
        if not self.detalle.strip():
            raise ValueError("La dirección no puede estar vacía")


@dataclass(kw_only=True)
class ItemPedido:
    accesorio: Accesorio
    cantidad: int
    precio_unitario_cop: int

    def __post_init__(self) -> None:
        if self.cantidad <= 0:
            raise PedidoInvalidoError("La cantidad debe ser mayor que cero")
        if self.precio_unitario_cop <= 0:
            raise PedidoInvalidoError("El precio unitario debe ser mayor que cero")

    @classmethod
    def desde_accesorio(cls, accesorio: Accesorio, cantidad: int) -> "ItemPedido":
        return cls(accesorio=accesorio, cantidad=cantidad, precio_unitario_cop=accesorio.precio_cop)

    def subtotal(self) -> int:
        return self.cantidad * self.precio_unitario_cop


@dataclass(kw_only=True)
class Pedido:
    id: int | None = None
    usuario: Usuario
    direccion: Direccion
    items: list[ItemPedido]
    estado: EstadoPedido = EstadoPedido.PENDIENTE_PAGO
    subtotal_cop: int
    costo_envio_cop: int
    creado_en: datetime
    reservado_hasta: datetime

    def __post_init__(self) -> None:
        if not self.items:
            raise PedidoInvalidoError("El pedido debe tener al menos un accesorio")
        if self.direccion.usuario.correo != self.usuario.correo:
            raise PedidoInvalidoError("La dirección no pertenece a este cliente")
        if self.subtotal_cop != sum(item.subtotal() for item in self.items):
            raise PedidoInvalidoError("El subtotal no coincide con los accesorios")

    @classmethod
    def crear(
        cls,
        usuario: Usuario,
        direccion: Direccion,
        items: list[ItemPedido],
        ahora: datetime,
        minutos_reserva: int = MINUTOS_RESERVA,
    ) -> "Pedido":
        return cls(
            usuario=usuario,
            direccion=direccion,
            items=items,
            subtotal_cop=sum(item.subtotal() for item in items),
            costo_envio_cop=direccion.municipio.departamento.costo_envio_cop,
            creado_en=ahora,
            reservado_hasta=ahora + timedelta(minutes=minutos_reserva),
        )

    def total_cop(self) -> int:
        return self.subtotal_cop + self.costo_envio_cop

    def reserva_vencida(self, ahora: datetime) -> bool:
        return self.estado == EstadoPedido.PENDIENTE_PAGO and ahora > self.reservado_hasta

    def marcar_pagado(self) -> None:
        if self.estado != EstadoPedido.PENDIENTE_PAGO:
            raise TransicionInvalidaError(f"No se puede pagar un pedido {self.estado.value}")
        self.estado = EstadoPedido.PAGADO

    def expirar(self) -> None:
        if self.estado != EstadoPedido.PENDIENTE_PAGO:
            raise TransicionInvalidaError(f"No se puede expirar un pedido {self.estado.value}")
        self.estado = EstadoPedido.EXPIRADO
