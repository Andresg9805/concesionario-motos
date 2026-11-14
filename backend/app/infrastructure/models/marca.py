from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.busqueda import Busqueda
    from app.infrastructure.models.moto import Moto
    from app.infrastructure.models.usuario import Usuario


class Marca(Base):
    __tablename__ = "marcas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    color_hex: Mapped[str] = mapped_column(String(7), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    motos: Mapped[list[Moto]] = relationship(back_populates="marca")
    usuarios_especialidad: Mapped[list[Usuario]] = relationship(back_populates="marca_especialidad")
    busquedas: Mapped[list[Busqueda]] = relationship(back_populates="marca")
