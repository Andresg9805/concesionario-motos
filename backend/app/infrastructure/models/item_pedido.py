
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.accesorio import Accesorio
    from app.infrastructure.models.pedido import Pedido


class ItemPedido(Base):
    __tablename__ = "items_pedido"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id"),
        nullable=False
    )

    accesorio_id: Mapped[int] = mapped_column(
        ForeignKey("accesorios.id"),
        nullable=False
    )

    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)

    precio_unitario_cop: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    pedido: Mapped[Pedido] = relationship(
        back_populates="items"
    )

    accesorio: Mapped[Accesorio] = relationship(
        back_populates="items_pedido"
    )
