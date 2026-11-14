from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.envio import Envio


class EventoEnvio(Base):
    __tablename__ = "eventos_envio"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    envio_id: Mapped[int] = mapped_column(ForeignKey("envios.id"), nullable=False)

    estado: Mapped[str] = mapped_column(
        Enum("PREPARANDO", "ENVIADO", "EN_CAMINO", "ENTREGADO", name="estado_evento_envio"),
        nullable=False,
    )

    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    nota: Mapped[str] = mapped_column(Text, nullable=False)

    envio: Mapped[Envio] = relationship(back_populates="eventos")
