from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.domain.excepciones import (
    PagoInvalidoError,
    PedidoInvalidoError,
    TransicionInvalidaError,
)
from app.domain.tienda import EstadoPedido, Pedido


class MetodoPago(StrEnum):
    TARJETA = "TARJETA"
    NEQUI = "NEQUI"
    PSE = "PSE"


class EstadoPago(StrEnum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    ERROR = "ERROR"


class EstadoEnvio(StrEnum):
    PREPARANDO = "PREPARANDO"
    ENVIADO = "ENVIADO"
    EN_CAMINO = "EN_CAMINO"
    ENTREGADO = "ENTREGADO"


ORDEN_ENVIO = list(EstadoEnvio)


@dataclass(frozen=True)
class ResultadoPago:
    referencia: str
    transaccion_id: str
    estado: EstadoPago
    monto_cop: int


@dataclass(kw_only=True)
class Pago:
    id: int | None = None
    pedido: Pedido
    referencia: str
    transaccion_id: str | None = None
    metodo: MetodoPago
    estado: EstadoPago = EstadoPago.PENDIENTE
    monto_cop: int

    def __post_init__(self) -> None:
        if not self.referencia.strip():
            raise PagoInvalidoError("El pago debe tener una referencia")
        if self.monto_cop != self.pedido.total_cop():
            raise PagoInvalidoError("El monto del pago no coincide con el total del pedido")

    @classmethod
    def para_pedido(cls, pedido: Pedido, referencia: str, metodo: MetodoPago) -> "Pago":
        return cls(
            pedido=pedido, referencia=referencia, metodo=metodo, monto_cop=pedido.total_cop()
        )

    def monto_en_centavos(self) -> int:
        return self.monto_cop * 100

    def aprobar(self, transaccion_id: str) -> None:
        if self.estado != EstadoPago.PENDIENTE:
            raise TransicionInvalidaError(f"No se puede aprobar un pago {self.estado.value}")
        self.transaccion_id = transaccion_id
        self.estado = EstadoPago.APROBADO

    def rechazar(self) -> None:
        if self.estado != EstadoPago.PENDIENTE:
            raise TransicionInvalidaError(f"No se puede rechazar un pago {self.estado.value}")
        self.estado = EstadoPago.RECHAZADO

    def actualizar_con(self, resultado: ResultadoPago) -> bool:
        if resultado.referencia != self.referencia:
            raise PagoInvalidoError("La referencia no corresponde a este pago")
        if resultado.monto_cop != self.monto_cop:
            raise PagoInvalidoError("El monto pagado no coincide con el del pedido")
        if resultado.estado == self.estado or resultado.estado == EstadoPago.PENDIENTE:
            return False
        if resultado.estado == EstadoPago.APROBADO:
            self.aprobar(resultado.transaccion_id)
        elif resultado.estado == EstadoPago.RECHAZADO:
            self.transaccion_id = resultado.transaccion_id
            self.rechazar()
        else:
            if self.estado != EstadoPago.PENDIENTE:
                raise TransicionInvalidaError(f"El pago ya está {self.estado.value}")
            self.transaccion_id = resultado.transaccion_id
            self.estado = EstadoPago.ERROR
        return True


@dataclass(kw_only=True)
class EventoEnvio:
    estado: EstadoEnvio
    fecha: datetime
    nota: str = ""


@dataclass(kw_only=True)
class Envio:
    id: int | None = None
    pedido: Pedido
    numero_guia: str
    costo_cop: int
    estado: EstadoEnvio = EstadoEnvio.PREPARANDO
    eventos: list[EventoEnvio] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.pedido.estado != EstadoPedido.PAGADO:
            raise PedidoInvalidoError("Solo se envían pedidos pagados")

    @classmethod
    def crear(cls, pedido: Pedido, numero_guia: str, fecha: datetime) -> "Envio":
        envio = cls(pedido=pedido, numero_guia=numero_guia, costo_cop=pedido.costo_envio_cop)
        envio.eventos.append(
            EventoEnvio(estado=EstadoEnvio.PREPARANDO, fecha=fecha, nota="Pago aprobado")
        )
        return envio

    def avanzar(self, nuevo: EstadoEnvio, nota: str, fecha: datetime) -> None:
        indice_actual = ORDEN_ENVIO.index(self.estado)
        if indice_actual + 1 >= len(ORDEN_ENVIO) or ORDEN_ENVIO[indice_actual + 1] != nuevo:
            raise TransicionInvalidaError(
                f"No se puede pasar de {self.estado.value} a {nuevo.value}"
            )
        self.estado = nuevo
        self.eventos.append(EventoEnvio(estado=nuevo, fecha=fecha, nota=nota))
