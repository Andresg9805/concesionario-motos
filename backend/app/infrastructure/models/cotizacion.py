
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.cliente import Cliente
    from app.infrastructure.models.moto import Moto
    from app.infrastructure.models.usuario import Usuario


class Cotizacion(Base):
    __tablename__ = "cotizaciones"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    codigo_seguimiento: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id"),
        nullable=False
    )

    moto_id: Mapped[int] = mapped_column(
        ForeignKey("motos.id"),
        nullable=False
    )

    asesor_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    precio_cop: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    cuota_inicial_cop: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    plazo_meses: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    tasa_mensual: Mapped[Decimal] = mapped_column(
        Numeric(7, 4),
        nullable=False
    )

    cuota_mensual_cop: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    estado_atencion: Mapped[str] = mapped_column(
        Enum(
            "nuevo",
            "contactado",
            "test_drive",
            "negociando",
            "vendido",
            "descartado",
            name="estado_atencion_cotizacion"
        ),
        nullable=False
    )

    cliente: Mapped[Cliente] = relationship(
        back_populates="cotizaciones"
    )

    moto: Mapped[Moto] = relationship(
        back_populates="cotizaciones"
    )

    asesor: Mapped[Usuario] = relationship(
    back_populates="cotizaciones"
    )
