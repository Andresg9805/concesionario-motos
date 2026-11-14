from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.marca import Marca


class Busqueda(Base):
    __tablename__ = "busquedas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    cuota_maxima_cop: Mapped[int] = mapped_column(Integer, nullable=False)
    cuota_inicial_cop: Mapped[int] = mapped_column(Integer, nullable=False)

    uso: Mapped[str] = mapped_column(
        Enum("CIUDAD", "CARRETERA", "TRABAJO", name="uso_busqueda"),
        nullable=False,
    )

    marca_id: Mapped[int | None] = mapped_column(
        ForeignKey("marcas.id"),
        nullable=True,
    )

    cantidad_resultados: Mapped[int] = mapped_column(Integer, nullable=False)

    marca: Mapped[Marca | None] = relationship(back_populates="busquedas")
