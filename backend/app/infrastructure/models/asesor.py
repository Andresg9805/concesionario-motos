from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.cotizacion import Cotizacion
    from app.infrastructure.models.marca import Marca
    from app.infrastructure.models.test_drive import TestDrive
    from app.infrastructure.models.usuario import Usuario


class Asesor(Base):
    __tablename__ = "asesores"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    marca_id: Mapped[int] = mapped_column(ForeignKey("marcas.id"), nullable=False)

    usuario: Mapped[Usuario] = relationship(back_populates="asesor")
    marca: Mapped[Marca] = relationship(back_populates="asesores")
    cotizaciones: Mapped[list[Cotizacion]] = relationship(back_populates="asesor")
    test_drives: Mapped[list[TestDrive]] = relationship(back_populates="asesor")
