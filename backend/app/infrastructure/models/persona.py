from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.cotizacion import Cotizacion
    from app.infrastructure.models.test_drive import TestDrive
    from app.infrastructure.models.usuario import Usuario


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    correo: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)

    usuario: Mapped[Usuario | None] = relationship(back_populates="persona", uselist=False)
    cotizaciones: Mapped[list[Cotizacion]] = relationship(back_populates="cliente")
    test_drives: Mapped[list[TestDrive]] = relationship(back_populates="cliente")
