from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.direccion import Direccion
    from app.infrastructure.models.envio import Envio
    from app.infrastructure.models.item_pedido import ItemPedido
    from app.infrastructure.models.pago import Pago
    from app.infrastructure.models.usuario import Usuario


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    direccion_id: Mapped[int] = mapped_column(ForeignKey("direcciones.id"), nullable=False)

    estado: Mapped[str] = mapped_column(
        Enum("PENDIENTE_PAGO", "PAGADO", "EXPIRADO", name="estado_pedido"), nullable=False
    )

    subtotal_cop: Mapped[int] = mapped_column(Integer, nullable=False)

    costo_envio_cop: Mapped[int] = mapped_column(Integer, nullable=False)

    total_cop: Mapped[int] = mapped_column(Integer, nullable=False)

    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    reservado_hasta: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    usuario: Mapped[Usuario] = relationship(back_populates="pedidos")

    direccion: Mapped[Direccion] = relationship(back_populates="pedidos")

    items: Mapped[list[ItemPedido]] = relationship(back_populates="pedido")

    pagos: Mapped[list[Pago]] = relationship(back_populates="pedido")

    envio: Mapped[Envio | None] = relationship(back_populates="pedido", uselist=False)
