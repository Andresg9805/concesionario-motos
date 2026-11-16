from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.asesor import Asesor
    from app.infrastructure.models.moto import Moto
    from app.infrastructure.models.persona import Persona


class Cotizacion(Base):
    __tablename__ = "cotizaciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    codigo_seguimiento: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    cliente_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), nullable=False)

    moto_id: Mapped[int] = mapped_column(ForeignKey("motos.id"), nullable=False)

    asesor_id: Mapped[int] = mapped_column(ForeignKey("asesores.usuario_id"), nullable=False)

    fecha: Mapped[date] = mapped_column(Date, nullable=False)

    precio_cop: Mapped[int] = mapped_column(Integer, nullable=False)

    cuota_inicial_cop: Mapped[int] = mapped_column(Integer, nullable=False)

    plazo_meses: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    tasa_mensual: Mapped[Decimal] = mapped_column(Numeric(7, 4), nullable=False)

    estado_atencion: Mapped[str] = mapped_column(
        Enum(
            "NUEVO",
            "CONTACTADO",
            "TEST_DRIVE",
            "NEGOCIANDO",
            "VENDIDO",
            "DESCARTADO",
            name="estado_atencion_cotizacion",
        ),
        nullable=False,
    )

    cliente: Mapped[Persona] = relationship(back_populates="cotizaciones")

    moto: Mapped[Moto] = relationship(back_populates="cotizaciones")

    asesor: Mapped[Asesor] = relationship(back_populates="cotizaciones")
