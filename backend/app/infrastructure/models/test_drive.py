from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.asesor import Asesor
    from app.infrastructure.models.moto import Moto
    from app.infrastructure.models.persona import Persona


class TestDrive(Base):
    __tablename__ = "test_drives"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    codigo_seguimiento: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    cliente_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), nullable=False)

    moto_id: Mapped[int] = mapped_column(ForeignKey("motos.id"), nullable=False)

    asesor_id: Mapped[int] = mapped_column(ForeignKey("asesores.usuario_id"), nullable=False)

    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    fecha_programada: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    estado: Mapped[str] = mapped_column(
        Enum("PENDIENTE", "PROGRAMADO", "REALIZADO", "CANCELADO", name="estado_test_drive"),
        nullable=False,
    )

    cliente: Mapped[Persona] = relationship(back_populates="test_drives")

    moto: Mapped[Moto] = relationship(back_populates="test_drives")

    asesor: Mapped[Asesor] = relationship(back_populates="test_drives")
