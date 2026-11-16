from collections.abc import Callable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.excepciones import StockInsuficienteError
from app.domain.pagos_envios import Envio, Pago
from app.domain.puertos import RepositorioEnvios, RepositorioPagos, RepositorioPedidos
from app.domain.tienda import EstadoPedido, Pedido
from app.infrastructure.db.repositorios.conversiones import (
    ZONA_COLOMBIA,
    envio_a_dominio,
    fecha_a_bd,
    pago_a_dominio,
    pedido_a_dominio,
)
from app.infrastructure.models.accesorio import Accesorio as AccesorioModelo
from app.infrastructure.models.direccion import Direccion as DireccionModelo
from app.infrastructure.models.envio import Envio as EnvioModelo
from app.infrastructure.models.evento_envio import EventoEnvio as EventoEnvioModelo
from app.infrastructure.models.evento_pago import EventoPago as EventoPagoModelo
from app.infrastructure.models.item_pedido import ItemPedido as ItemPedidoModelo
from app.infrastructure.models.pago import Pago as PagoModelo
from app.infrastructure.models.pedido import Pedido as PedidoModelo

Reloj = Callable[[], datetime]


def reloj_colombia() -> datetime:
    return datetime.now(ZONA_COLOMBIA)


class RepositorioPedidosSQLAlchemy(RepositorioPedidos):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def crear_con_reserva(self, pedido: Pedido) -> Pedido:
        return self._insertar(pedido, reservar=True)

    def _insertar(self, pedido: Pedido, reservar: bool) -> Pedido:
        punto = self.sesion.begin_nested()
        try:
            modelo = PedidoModelo(
                usuario_id=pedido.usuario.id,
                direccion_id=pedido.direccion.id,
                estado=pedido.estado.value,
                costo_envio_cop=pedido.costo_envio_cop,
                creado_en=fecha_a_bd(pedido.creado_en),
                reservado_hasta=fecha_a_bd(pedido.reservado_hasta),
            )
            self.sesion.add(modelo)
            for item in pedido.items:
                accesorio = self.sesion.get(AccesorioModelo, item.accesorio.id or 0)
                if accesorio is None:
                    raise StockInsuficienteError(f"No existe {item.accesorio.nombre}")
                if reservar:
                    if accesorio.stock < item.cantidad:
                        raise StockInsuficienteError(
                            f"No hay stock suficiente de {item.accesorio.nombre}"
                        )
                    accesorio.stock -= item.cantidad
                modelo.items.append(
                    ItemPedidoModelo(
                        accesorio=accesorio,
                        cantidad=item.cantidad,
                        precio_unitario_cop=item.precio_unitario_cop,
                    )
                )
            self.sesion.flush()
            punto.commit()
        except Exception:
            punto.rollback()
            raise

        self.sesion.refresh(modelo)
        pedido.id = modelo.id
        return pedido_a_dominio(modelo)

    def buscar_por_id(self, id: int) -> Pedido | None:
        modelo = self.sesion.get(PedidoModelo, id)
        return None if modelo is None else pedido_a_dominio(modelo)

    def guardar(self, pedido: Pedido) -> Pedido:
        if pedido.id is None:
            return self._insertar(pedido, reservar=False)
        modelo = self.sesion.get(PedidoModelo, pedido.id)
        if modelo is None:
            raise ValueError("El pedido indicado no existe en la base de datos")
        if self.sesion.get(DireccionModelo, pedido.direccion.id or 0) is None:
            raise ValueError("La dirección indicada no existe en la base de datos")

        modelo.direccion_id = pedido.direccion.id or 0
        modelo.estado = pedido.estado.value
        modelo.costo_envio_cop = pedido.costo_envio_cop
        modelo.reservado_hasta = fecha_a_bd(pedido.reservado_hasta)

        self.sesion.flush()
        return pedido_a_dominio(modelo)

    def listar_por_usuario(self, usuario_id: int) -> list[Pedido]:
        modelos = self.sesion.scalars(
            select(PedidoModelo)
            .where(PedidoModelo.usuario_id == usuario_id)
            .order_by(PedidoModelo.creado_en.desc(), PedidoModelo.id.desc())
        ).all()
        return [pedido_a_dominio(modelo) for modelo in modelos]

    def listar(self) -> list[Pedido]:
        modelos = self.sesion.scalars(select(PedidoModelo).order_by(PedidoModelo.id)).all()
        return [pedido_a_dominio(modelo) for modelo in modelos]

    def listar_vencidos(self, ahora: datetime) -> list[Pedido]:
        modelos = self.sesion.scalars(
            select(PedidoModelo)
            .where(
                PedidoModelo.estado == EstadoPedido.PENDIENTE_PAGO.value,
                PedidoModelo.reservado_hasta < fecha_a_bd(ahora),
            )
            .order_by(PedidoModelo.reservado_hasta, PedidoModelo.id)
        ).all()
        return [pedido_a_dominio(modelo) for modelo in modelos]


class RepositorioPagosSQLAlchemy(RepositorioPagos):
    def __init__(self, sesion: Session, reloj: Reloj = reloj_colombia):
        self.sesion = sesion
        self.reloj = reloj

    def guardar(self, pago: Pago) -> Pago:
        ahora = fecha_a_bd(self.reloj())
        if pago.id is None:
            if self.sesion.get(PedidoModelo, pago.pedido.id or 0) is None:
                raise ValueError("El pedido indicado no existe en la base de datos")
            modelo = PagoModelo(pedido_id=pago.pedido.id, creado_en=ahora)
            self.sesion.add(modelo)
        else:
            existente = self.sesion.get(PagoModelo, pago.id)
            if existente is None:
                raise ValueError("El pago indicado no existe en la base de datos")
            modelo = existente

        modelo.referencia = pago.referencia
        modelo.transaccion_id = pago.transaccion_id
        modelo.metodo = pago.metodo.value
        modelo.estado = pago.estado.value
        modelo.monto_cop = pago.monto_cop
        modelo.actualizado_en = ahora

        self.sesion.flush()
        self.sesion.refresh(modelo)
        pago.id = modelo.id
        return pago_a_dominio(modelo)

    def buscar_por_referencia(self, referencia: str) -> Pago | None:
        modelo = self.sesion.scalar(select(PagoModelo).where(PagoModelo.referencia == referencia))
        return None if modelo is None else pago_a_dominio(modelo)

    def buscar_por_pedido(self, pedido_id: int) -> Pago | None:
        modelo = self.sesion.scalar(
            select(PagoModelo)
            .where(PagoModelo.pedido_id == pedido_id)
            .order_by(PagoModelo.id.desc())
        )
        return None if modelo is None else pago_a_dominio(modelo)

    def registrar_evento(self, pago_id: int, checksum: str) -> bool:
        pago = self.sesion.get(PagoModelo, pago_id)
        if pago is None:
            raise ValueError("El pago indicado no existe en la base de datos")
        repetido = self.sesion.scalar(
            select(EventoPagoModelo).where(EventoPagoModelo.checksum == checksum)
        )
        if repetido is not None:
            return False

        punto = self.sesion.begin_nested()
        try:
            self.sesion.add(
                EventoPagoModelo(
                    pago_id=pago_id,
                    checksum=checksum,
                    estado_recibido=pago.estado,
                    recibido_en=fecha_a_bd(self.reloj()),
                )
            )
            self.sesion.flush()
            punto.commit()
        except IntegrityError:
            punto.rollback()
            return False
        return True


class RepositorioEnviosSQLAlchemy(RepositorioEnvios):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, envio: Envio) -> Envio:
        if envio.id is None:
            if self.sesion.get(PedidoModelo, envio.pedido.id or 0) is None:
                raise ValueError("El pedido indicado no existe en la base de datos")
            creado_en = envio.eventos[0].fecha if envio.eventos else reloj_colombia()
            modelo = EnvioModelo(
                pedido_id=envio.pedido.id,
                numero_guia=envio.numero_guia,
                creado_en=fecha_a_bd(creado_en),
            )
            self.sesion.add(modelo)
        else:
            existente = self.sesion.get(EnvioModelo, envio.id)
            if existente is None:
                raise ValueError("El envío indicado no existe en la base de datos")
            modelo = existente

        modelo.numero_guia = envio.numero_guia
        guardados = len(modelo.eventos)
        for evento in envio.eventos[guardados:]:
            modelo.eventos.append(
                EventoEnvioModelo(
                    estado=evento.estado.value,
                    fecha=fecha_a_bd(evento.fecha),
                    nota=evento.nota,
                )
            )

        self.sesion.flush()
        self.sesion.refresh(modelo)
        envio.id = modelo.id
        return envio_a_dominio(modelo)

    def buscar_por_id(self, id: int) -> Envio | None:
        modelo = self.sesion.get(EnvioModelo, id)
        return None if modelo is None else envio_a_dominio(modelo)

    def buscar_por_pedido(self, pedido_id: int) -> Envio | None:
        modelo = self.sesion.scalar(select(EnvioModelo).where(EnvioModelo.pedido_id == pedido_id))
        return None if modelo is None else envio_a_dominio(modelo)

    def listar(self) -> list[Envio]:
        modelos = self.sesion.scalars(select(EnvioModelo).order_by(EnvioModelo.id)).all()
        return [envio_a_dominio(modelo) for modelo in modelos]
