from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.evento_pago import EventoPago
    from app.infrastructure.models.pedido import Pedido


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)

    referencia: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    transaccion_id: Mapped[str] = mapped_column(String, nullable=False)

    metodo: Mapped[str] = mapped_column(
        Enum("TARJETA", "NEQUI", "PSE", name="metodo_pago"), nullable=False
    )

    estado: Mapped[str] = mapped_column(
        Enum("PENDIENTE", "APROBADO", "RECHAZADO", "ERROR", name="estado_pago"), nullable=False
    )

    monto_cop: Mapped[int] = mapped_column(Integer, nullable=False)

    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    actualizado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    pedido: Mapped[Pedido] = relationship(back_populates="pagos")

    eventos: Mapped[list[EventoPago]] = relationship(back_populates="pago")
