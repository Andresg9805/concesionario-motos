
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.compatibilidad import Compatibilidad
    from app.infrastructure.models.item_pedido import ItemPedido


class Accesorio(Base):
    __tablename__ = "accesorios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    sku: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    nombre: Mapped[str] = mapped_column(String, nullable=False)

    categoria: Mapped[str] = mapped_column(
        Enum(
            "mantenimiento",
            "chaqueta",
            "casco",
            "guantes",
            "maleta",
            "rodillera",
            "hombrera",
            name="categoria_accesorio"
        ),
        nullable=False
    )

    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    precio_cop: Mapped[int] = mapped_column(Integer, nullable=False)

    stock: Mapped[int] = mapped_column(Integer, nullable=False)

    imagen_url: Mapped[str] = mapped_column(String, nullable=False)

    items_pedido: Mapped[list[ItemPedido]] = relationship(
        back_populates="accesorio"
    )

    compatibilidades: Mapped[list[Compatibilidad]] = relationship(
        back_populates="accesorio"
    )
