from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CHAR, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.departamento import Departamento
    from app.infrastructure.models.direccion import Direccion


class Municipio(Base):
    __tablename__ = "municipios"

    codigo: Mapped[str] = mapped_column(CHAR(5), primary_key=True)

    nombre: Mapped[str] = mapped_column(String, nullable=False)

    departamento_codigo: Mapped[str] = mapped_column(
        CHAR(2), ForeignKey("departamentos.codigo"), nullable=False
    )

    departamento: Mapped[Departamento] = relationship(back_populates="municipios")

    direcciones: Mapped[list[Direccion]] = relationship(back_populates="municipio")
