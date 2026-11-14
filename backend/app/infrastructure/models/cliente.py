from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.cotizacion import Cotizacion
    from app.infrastructure.models.test_drive import TestDrive
    from app.infrastructure.models.usuario import Usuario


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    nombre: Mapped[str] = mapped_column(String, nullable=False)

    correo: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    telefono: Mapped[str] = mapped_column(String, nullable=False)

    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"), unique=True, nullable=True
    )

    cotizaciones: Mapped[list[Cotizacion]] = relationship(back_populates="cliente")

    test_drives: Mapped[list[TestDrive]] = relationship(back_populates="cliente")

    usuario: Mapped[Usuario | None] = relationship(back_populates="cliente")
