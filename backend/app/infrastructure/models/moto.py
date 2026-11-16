from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.cotizacion import Cotizacion
    from app.infrastructure.models.marca import Marca
    from app.infrastructure.models.test_drive import TestDrive
    from app.infrastructure.models.tipo_moto import TipoMoto


class Moto(Base):
    __tablename__ = "motos"
    __table_args__ = (
        UniqueConstraint("marca_id", "modelo", "anio", name="uq_moto_marca_modelo_anio"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    marca_id: Mapped[int] = mapped_column(ForeignKey("marcas.id"), nullable=False)
    tipo_id: Mapped[int] = mapped_column(ForeignKey("tipos_moto.id"), nullable=False)
    modelo: Mapped[str] = mapped_column(String, nullable=False)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cilindraje_cc: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_cop: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    consumo_km_galon: Mapped[float] = mapped_column(Float, nullable=False)
    costo_mantenimiento_km_cop: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    imagen_url: Mapped[str] = mapped_column(String, nullable=False)

    marca: Mapped[Marca] = relationship(back_populates="motos")
    tipo: Mapped[TipoMoto] = relationship(back_populates="motos")
    cotizaciones: Mapped[list[Cotizacion]] = relationship(back_populates="moto")
    test_drives: Mapped[list[TestDrive]] = relationship(back_populates="moto")
