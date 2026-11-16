from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.asesor import Asesor
    from app.infrastructure.models.busqueda import Busqueda
    from app.infrastructure.models.moto import Moto


class Marca(Base):
    __tablename__ = "marcas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    color_hex: Mapped[str] = mapped_column(String(7), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    motos: Mapped[list[Moto]] = relationship(back_populates="marca")
    asesores: Mapped[list[Asesor]] = relationship(back_populates="marca")
    busquedas: Mapped[list[Busqueda]] = relationship(back_populates="marca")
