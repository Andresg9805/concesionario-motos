from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.accesorio import Accesorio
    from app.infrastructure.models.moto import Moto


class Compatibilidad(Base):
    __tablename__ = "compatibilidades"

    accesorio_id: Mapped[int] = mapped_column(ForeignKey("accesorios.id"), primary_key=True)

    moto_id: Mapped[int] = mapped_column(ForeignKey("motos.id"), primary_key=True)

    accesorio: Mapped[Accesorio] = relationship(back_populates="compatibilidades")

    moto: Mapped[Moto] = relationship(back_populates="compatibilidades")
