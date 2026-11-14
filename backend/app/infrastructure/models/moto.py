
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.compatibilidad import Compatibilidad
    from app.infrastructure.models.cotizacion import Cotizacion
    from app.infrastructure.models.marca import Marca
    from app.infrastructure.models.test_drive import TestDrive



class Moto(Base):
    __tablename__ = "motos"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    marca_id: Mapped[int] = mapped_column(
        ForeignKey("marcas.id"),
        nullable=False
    )

    modelo: Mapped[str] = mapped_column(String, nullable=False)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cilindraje_cc: Mapped[int] = mapped_column(Integer, nullable=False)

    tipo: Mapped[str] = mapped_column(
        Enum("naked", "deportiva", "trail", "doble_proposito", name="tipo_moto"),
        nullable=False
    )

    categoria_licencia: Mapped[str] = mapped_column(
        Enum("A1", "A2", name="categoria_licencia"),
        nullable=False
    )

    precio_cop: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    consumo_km_galon: Mapped[float] = mapped_column(Float, nullable=False)

    costo_mantenimiento_km_cop: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    imagen_url: Mapped[str] = mapped_column(String, nullable=False)

    marca: Mapped[Marca] = relationship(
        back_populates="motos"
    )

    cotizaciones: Mapped[list[Cotizacion]] = relationship(
        back_populates="moto"
    )

    test_drives: Mapped[list[TestDrive]] = relationship(
    back_populates="moto"
    )

    compatibilidades: Mapped[list[Compatibilidad]] = relationship(
        back_populates="moto"
    )
