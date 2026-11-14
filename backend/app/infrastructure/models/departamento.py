
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CHAR, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.municipio import Municipio


class Departamento(Base):
    __tablename__ = "departamentos"

    codigo: Mapped[str] = mapped_column(CHAR(2), primary_key=True)

    nombre: Mapped[str] = mapped_column(String, nullable=False)

    costo_envio_cop: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    dias_envio: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    municipios: Mapped[list[Municipio]] = relationship(
        back_populates="departamento"
    )
