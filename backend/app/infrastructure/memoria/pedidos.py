from datetime import datetime
from itertools import count
from threading import Lock

from app.domain.excepciones import StockInsuficienteError
from app.domain.pagos_envios import Envio, Pago
from app.domain.puertos import (
    RepositorioAccesorios,
    RepositorioEnvios,
    RepositorioPagos,
    RepositorioPedidos,
)
from app.domain.tienda import Pedido


class RepositorioPedidosEnMemoria(RepositorioPedidos):
    def __init__(self, accesorios: RepositorioAccesorios) -> None:
        self._accesorios = accesorios
        self._pedidos: dict[int, Pedido] = {}
        self._ids = count(1)
        self._candado = Lock()

    def crear_con_reserva(self, pedido: Pedido) -> Pedido:
        with self._candado:
            for item in pedido.items:
                actual = self._accesorios.buscar_por_id(item.accesorio.id or 0)
                if actual is None or not actual.hay_stock(item.cantidad):
                    raise StockInsuficienteError(
                        f"No hay stock suficiente de {item.accesorio.nombre}"
                    )
            for item in pedido.items:
                actual = self._accesorios.buscar_por_id(item.accesorio.id or 0)
                if actual is None:
                    raise StockInsuficienteError(f"No existe {item.accesorio.nombre}")
                actual.reservar(item.cantidad)
                self._accesorios.guardar(actual)
            pedido.id = next(self._ids)
            self._pedidos[pedido.id] = pedido
            return pedido

    def buscar_por_id(self, id: int) -> Pedido | None:
        with self._candado:
            return self._pedidos.get(id)

    def guardar(self, pedido: Pedido) -> Pedido:
        with self._candado:
            if pedido.id is None:
                pedido.id = next(self._ids)
            self._pedidos[pedido.id] = pedido
            return pedido

    def listar_por_usuario(self, usuario_id: int) -> list[Pedido]:
        with self._candado:
            return [pedido for pedido in self._pedidos.values() if pedido.usuario.id == usuario_id]

    def listar_vencidos(self, ahora: datetime) -> list[Pedido]:
        with self._candado:
            return [pedido for pedido in self._pedidos.values() if pedido.reserva_vencida(ahora)]


class RepositorioPagosEnMemoria(RepositorioPagos):
    def __init__(self) -> None:
        self._pagos: dict[int, Pago] = {}
        self._eventos: dict[str, int] = {}
        self._ids = count(1)
        self._candado = Lock()

    def guardar(self, pago: Pago) -> Pago:
        with self._candado:
            if pago.id is None:
                pago.id = next(self._ids)
            self._pagos[pago.id] = pago
            return pago

    def buscar_por_referencia(self, referencia: str) -> Pago | None:
        with self._candado:
            return next(
                (pago for pago in self._pagos.values() if pago.referencia == referencia), None
            )

    def buscar_por_pedido(self, pedido_id: int) -> Pago | None:
        with self._candado:
            coincidencias = [pago for pago in self._pagos.values() if pago.pedido.id == pedido_id]
            return coincidencias[-1] if coincidencias else None

    def registrar_evento(self, pago_id: int, checksum: str) -> bool:
        with self._candado:
            if checksum in self._eventos:
                return False
            self._eventos[checksum] = pago_id
            return True


class RepositorioEnviosEnMemoria(RepositorioEnvios):
    def __init__(self) -> None:
        self._envios: dict[int, Envio] = {}
        self._ids = count(1)
        self._candado = Lock()

    def guardar(self, envio: Envio) -> Envio:
        with self._candado:
            if envio.id is None:
                envio.id = next(self._ids)
            self._envios[envio.id] = envio
            return envio

    def buscar_por_pedido(self, pedido_id: int) -> Envio | None:
        with self._candado:
            return next(
                (envio for envio in self._envios.values() if envio.pedido.id == pedido_id), None
            )

    def listar(self) -> list[Envio]:
        with self._candado:
            return list(self._envios.values())
