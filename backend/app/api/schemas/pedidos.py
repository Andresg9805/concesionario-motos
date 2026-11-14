from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.api.schemas.auth import EntradaEstricta
from app.application.pedidos import VistaPedido
from app.domain.pagos_envios import EstadoEnvio, EstadoPago, EventoEnvio
from app.domain.tienda import EstadoPedido, ItemPedido, Pedido

MAXIMO_ITEMS = 50
MAXIMA_CANTIDAD = 99


class ItemPedidoEntrada(EntradaEstricta):
    accesorio_id: int = Field(ge=1, examples=[7])
    cantidad: int = Field(ge=1, le=MAXIMA_CANTIDAD, examples=[2])


class PedidoEntrada(EntradaEstricta):
    direccion_id: int = Field(ge=1, examples=[5])
    items: list[ItemPedidoEntrada] = Field(min_length=1, max_length=MAXIMO_ITEMS)


class VerificarPagoEntrada(EntradaEstricta):
    transaccion_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9_-]+$",
        examples=["12345-1731700000-12345"],
    )


class WompiSalida(BaseModel):
    llave_publica: str
    referencia: str
    monto_centavos: int
    moneda: str
    firma_integridad: str

    @classmethod
    def desde_datos(cls, datos: dict[str, Any]) -> "WompiSalida":
        return cls(**datos)


class PedidoCreadoSalida(BaseModel):
    pedido_id: int
    total_cop: int
    reservado_hasta: datetime
    wompi: WompiSalida


def reserva_visible(pedido: Pedido) -> datetime | None:
    return None if pedido.estado == EstadoPedido.PAGADO else pedido.reservado_hasta


class VerificarPagoSalida(BaseModel):
    pedido_id: int
    estado_pago: EstadoPago
    estado_pedido: EstadoPedido
    total_cop: int
    numero_guia: str | None
    reservado_hasta: datetime | None

    @classmethod
    def desde_vista(cls, vista: VistaPedido) -> "VerificarPagoSalida":
        return cls(
            pedido_id=vista.pedido.id or 0,
            estado_pago=vista.pago.estado if vista.pago else EstadoPago.PENDIENTE,
            estado_pedido=vista.pedido.estado,
            total_cop=vista.pedido.total_cop(),
            numero_guia=vista.envio.numero_guia if vista.envio else None,
            reservado_hasta=reserva_visible(vista.pedido),
        )


class ItemPedidoSalida(BaseModel):
    accesorio_id: int
    nombre: str
    cantidad: int
    precio_unitario_cop: int
    subtotal_cop: int

    @classmethod
    def desde_dominio(cls, item: ItemPedido) -> "ItemPedidoSalida":
        return cls(
            accesorio_id=item.accesorio.id or 0,
            nombre=item.accesorio.nombre,
            cantidad=item.cantidad,
            precio_unitario_cop=item.precio_unitario_cop,
            subtotal_cop=item.subtotal(),
        )


class EventoEnvioSalida(BaseModel):
    estado: EstadoEnvio
    fecha: datetime
    nota: str

    @classmethod
    def desde_dominio(cls, evento: EventoEnvio) -> "EventoEnvioSalida":
        return cls(estado=evento.estado, fecha=evento.fecha, nota=evento.nota)


class PedidoResumenSalida(VerificarPagoSalida):
    subtotal_cop: int
    costo_envio_cop: int
    creado_en: datetime

    @classmethod
    def desde_vista(cls, vista: VistaPedido) -> "PedidoResumenSalida":
        base = VerificarPagoSalida.desde_vista(vista)
        return cls(
            **base.model_dump(),
            subtotal_cop=vista.pedido.subtotal_cop,
            costo_envio_cop=vista.pedido.costo_envio_cop,
            creado_en=vista.pedido.creado_en,
        )


class PedidoDetalleSalida(PedidoResumenSalida):
    items: list[ItemPedidoSalida]
    estado_envio: EstadoEnvio | None
    eventos: list[EventoEnvioSalida]

    @classmethod
    def desde_vista(cls, vista: VistaPedido) -> "PedidoDetalleSalida":
        resumen = PedidoResumenSalida.desde_vista(vista)
        envio = vista.envio
        return cls(
            **resumen.model_dump(),
            items=[ItemPedidoSalida.desde_dominio(item) for item in vista.pedido.items],
            estado_envio=envio.estado if envio else None,
            eventos=[EventoEnvioSalida.desde_dominio(e) for e in envio.eventos] if envio else [],
        )
