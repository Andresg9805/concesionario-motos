from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.cliente import Cliente
    from app.infrastructure.models.moto import Moto
    from app.infrastructure.models.usuario import Usuario


class TestDrive(Base):
    __tablename__ = "test_drives"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    codigo_seguimiento: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)

    moto_id: Mapped[int] = mapped_column(ForeignKey("motos.id"), nullable=False)

    asesor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    fecha_programada: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    estado: Mapped[str] = mapped_column(
        Enum("PENDIENTE", "PROGRAMADO", "REALIZADO", "CANCELADO", name="estado_test_drive"),
        nullable=False,
    )

    cliente: Mapped[Cliente] = relationship(back_populates="test_drives")

    moto: Mapped[Moto] = relationship(back_populates="test_drives")

    asesor: Mapped[Usuario] = relationship(back_populates="test_drives")
