
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.evento_envio import EventoEnvio
    from app.infrastructure.models.pedido import Pedido


class Envio(Base):
    __tablename__ = "envios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id"),
        unique=True,
        nullable=False
    )

    numero_guia: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    costo_cop: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        Enum(
            "preparando",
            "enviado",
            "en_camino",
            "entregado",
            name="estado_envio"
        ),
        nullable=False
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    pedido: Mapped[Pedido] = relationship(
        back_populates="envio"
    )

    eventos: Mapped[list[EventoEnvio]] = relationship(
        back_populates="envio"
    )
