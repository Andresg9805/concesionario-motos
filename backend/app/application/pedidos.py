from dataclasses import dataclass
from threading import Lock
from typing import Any

from app.application.atencion import Reloj
from app.domain.excepciones import EntidadNoEncontradaError, StockInsuficienteError
from app.domain.pagos_envios import Envio, EstadoPago, MetodoPago, Pago, ResultadoPago
from app.domain.puertos import (
    PasarelaPago,
    RepositorioAccesorios,
    RepositorioDirecciones,
    RepositorioEnvios,
    RepositorioPagos,
    RepositorioPedidos,
    RepositorioUsuarios,
)
from app.domain.tienda import MINUTOS_RESERVA, EstadoPedido, ItemPedido, Pedido

PREFIJO_REFERENCIA = "CM-PED"
PREFIJO_GUIA = "CM-ENV"
DIGITOS_GUIA = 6


@dataclass(frozen=True)
class DatosItem:
    accesorio_id: int
    cantidad: int


@dataclass(frozen=True)
class VistaPedido:
    pedido: Pedido
    pago: Pago | None
    envio: Envio | None


@dataclass(frozen=True)
class PedidoCreado:
    pedido: Pedido
    datos_widget: dict[str, Any]


def numero_guia_de(pedido: Pedido) -> str:
    return f"{PREFIJO_GUIA}-{pedido.id or 0:0{DIGITOS_GUIA}d}"


class ExpirarReservas:
    def __init__(
        self, pedidos: RepositorioPedidos, accesorios: RepositorioAccesorios, reloj: Reloj
    ) -> None:
        self._pedidos = pedidos
        self._accesorios = accesorios
        self._reloj = reloj

    def ejecutar(self) -> None:
        for pedido in self._pedidos.listar_vencidos(self._reloj()):
            pedido.expirar()
            self._pedidos.guardar(pedido)
            for item in pedido.items:
                accesorio = self._accesorios.buscar_por_id(item.accesorio.id or 0)
                if accesorio is not None:
                    accesorio.liberar(item.cantidad)
                    self._accesorios.guardar(accesorio)


class ConfirmarPago:
    _candado = Lock()

    def __init__(
        self,
        pagos: RepositorioPagos,
        pedidos: RepositorioPedidos,
        envios: RepositorioEnvios,
        reloj: Reloj,
    ) -> None:
        self._pagos = pagos
        self._pedidos = pedidos
        self._envios = envios
        self._reloj = reloj

    def aplicar(self, pago: Pago, resultado: ResultadoPago) -> Envio | None:
        with self._candado:
            if pago.actualizar_con(resultado):
                self._pagos.guardar(pago)
            pedido = pago.pedido
            if pago.estado == EstadoPago.APROBADO and pedido.estado == EstadoPedido.PENDIENTE_PAGO:
                pedido.marcar_pagado()
                self._pedidos.guardar(pedido)
            if pedido.id is None:
                return None
            envio = self._envios.buscar_por_pedido(pedido.id)
            if envio is None and pedido.estado == EstadoPedido.PAGADO:
                envio = self._envios.guardar(
                    Envio.crear(pedido, numero_guia_de(pedido), self._reloj())
                )
            return envio


class CrearPedido:
    def __init__(
        self,
        usuarios: RepositorioUsuarios,
        direcciones: RepositorioDirecciones,
        accesorios: RepositorioAccesorios,
        pedidos: RepositorioPedidos,
        pagos: RepositorioPagos,
        pasarela: PasarelaPago,
        expirar_reservas: ExpirarReservas,
        reloj: Reloj,
        minutos_reserva: int = MINUTOS_RESERVA,
    ) -> None:
        self._usuarios = usuarios
        self._direcciones = direcciones
        self._accesorios = accesorios
        self._pedidos = pedidos
        self._pagos = pagos
        self._pasarela = pasarela
        self._expirar_reservas = expirar_reservas
        self._reloj = reloj
        self._minutos_reserva = minutos_reserva

    def ejecutar(self, usuario_id: int, direccion_id: int, items: list[DatosItem]) -> PedidoCreado:
        self._expirar_reservas.ejecutar()
        usuario = self._usuarios.buscar_por_id(usuario_id)
        if usuario is None:
            raise EntidadNoEncontradaError("No existe el usuario de la sesión")
        direccion = self._direcciones.buscar_por_id(direccion_id)
        if direccion is None or direccion.usuario.id != usuario_id:
            raise EntidadNoEncontradaError(f"No existe una dirección con id {direccion_id}")
        cantidades: dict[int, int] = {}
        for item in items:
            cantidades[item.accesorio_id] = cantidades.get(item.accesorio_id, 0) + item.cantidad
        lineas: list[ItemPedido] = []
        for accesorio_id, cantidad in cantidades.items():
            accesorio = self._accesorios.buscar_por_id(accesorio_id)
            if accesorio is None:
                raise StockInsuficienteError(f"No existe un accesorio con id {accesorio_id}")
            if not accesorio.hay_stock(cantidad):
                raise StockInsuficienteError(
                    f"Solo hay {accesorio.stock} unidades de {accesorio.nombre}"
                )
            lineas.append(ItemPedido.desde_accesorio(accesorio, cantidad))
        ahora = self._reloj()
        pedido = self._pedidos.crear_con_reserva(
            Pedido.crear(usuario, direccion, lineas, ahora, self._minutos_reserva)
        )
        referencia = f"{PREFIJO_REFERENCIA}-{pedido.id}-{int(ahora.timestamp())}"
        pago = self._pagos.guardar(Pago.para_pedido(pedido, referencia, MetodoPago.TARJETA))
        return PedidoCreado(pedido=pedido, datos_widget=self._pasarela.datos_para_widget(pago))


class VerificarPago:
    def __init__(
        self,
        pedidos: RepositorioPedidos,
        pagos: RepositorioPagos,
        envios: RepositorioEnvios,
        pasarela: PasarelaPago,
        confirmar_pago: ConfirmarPago,
    ) -> None:
        self._pedidos = pedidos
        self._pagos = pagos
        self._envios = envios
        self._pasarela = pasarela
        self._confirmar_pago = confirmar_pago

    def ejecutar(self, usuario_id: int, pedido_id: int, transaccion_id: str | None) -> VistaPedido:
        pedido = self._pedidos.buscar_por_id(pedido_id)
        if pedido is None or pedido.usuario.id != usuario_id:
            raise EntidadNoEncontradaError(f"No existe un pedido con id {pedido_id}")
        pago = self._pagos.buscar_por_pedido(pedido_id)
        if pago is None:
            raise EntidadNoEncontradaError(f"El pedido {pedido_id} no tiene un pago registrado")
        identificador = transaccion_id or pago.transaccion_id
        if identificador is not None:
            resultado = self._pasarela.consultar_transaccion(identificador)
            self._confirmar_pago.aplicar(pago, resultado)
        return VistaPedido(
            pedido=pedido, pago=pago, envio=self._envios.buscar_por_pedido(pedido_id)
        )


class ProcesarEventoPago:
    def __init__(
        self, pagos: RepositorioPagos, pasarela: PasarelaPago, confirmar_pago: ConfirmarPago
    ) -> None:
        self._pagos = pagos
        self._pasarela = pasarela
        self._confirmar_pago = confirmar_pago

    def ejecutar(self, cuerpo: dict[str, Any]) -> bool:
        resultado = self._pasarela.leer_evento(cuerpo)
        checksum = str(cuerpo["signature"]["checksum"])
        pago = self._pagos.buscar_por_referencia(resultado.referencia)
        if pago is None or pago.id is None:
            raise EntidadNoEncontradaError("No existe un pago con esa referencia")
        if not self._pagos.registrar_evento(pago.id, checksum):
            return False
        self._confirmar_pago.aplicar(pago, resultado)
        return True


class ListarPedidosPropios:
    def __init__(
        self,
        pedidos: RepositorioPedidos,
        pagos: RepositorioPagos,
        envios: RepositorioEnvios,
        expirar_reservas: ExpirarReservas,
    ) -> None:
        self._pedidos = pedidos
        self._pagos = pagos
        self._envios = envios
        self._expirar_reservas = expirar_reservas

    def ejecutar(self, usuario_id: int) -> list[VistaPedido]:
        self._expirar_reservas.ejecutar()
        propios = sorted(
            self._pedidos.listar_por_usuario(usuario_id),
            key=lambda pedido: pedido.id or 0,
            reverse=True,
        )
        return [
            VistaPedido(
                pedido=pedido,
                pago=self._pagos.buscar_por_pedido(pedido.id or 0),
                envio=self._envios.buscar_por_pedido(pedido.id or 0),
            )
            for pedido in propios
        ]


class ObtenerPedidoPropio:
    def __init__(
        self,
        pedidos: RepositorioPedidos,
        pagos: RepositorioPagos,
        envios: RepositorioEnvios,
        expirar_reservas: ExpirarReservas,
    ) -> None:
        self._pedidos = pedidos
        self._pagos = pagos
        self._envios = envios
        self._expirar_reservas = expirar_reservas

    def ejecutar(self, usuario_id: int, pedido_id: int) -> VistaPedido:
        self._expirar_reservas.ejecutar()
        pedido = self._pedidos.buscar_por_id(pedido_id)
        if pedido is None or pedido.usuario.id != usuario_id:
            raise EntidadNoEncontradaError(f"No existe un pedido con id {pedido_id}")
        return VistaPedido(
            pedido=pedido,
            pago=self._pagos.buscar_por_pedido(pedido_id),
            envio=self._envios.buscar_por_pedido(pedido_id),
        )
