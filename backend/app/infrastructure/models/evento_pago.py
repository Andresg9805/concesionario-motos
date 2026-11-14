
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.pago import Pago


class EventoPago(Base):
    __tablename__ = "eventos_pago"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    pago_id: Mapped[int] = mapped_column(
        ForeignKey("pagos.id"),
        nullable=False
    )

    checksum: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    estado_recibido: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    recibido_en: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    pago: Mapped[Pago] = relationship(
        back_populates="eventos"
    )
