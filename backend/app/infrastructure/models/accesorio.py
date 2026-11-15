from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.categoria_accesorio import CategoriaAccesorio
    from app.infrastructure.models.fabricante import Fabricante
    from app.infrastructure.models.item_pedido import ItemPedido


class Accesorio(Base):
    __tablename__ = "accesorios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias_accesorio.id"), nullable=False)
    fabricante_id: Mapped[int] = mapped_column(ForeignKey("fabricantes.id"), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    precio_cop: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    imagen_url: Mapped[str] = mapped_column(String, nullable=False)

    categoria: Mapped[CategoriaAccesorio] = relationship(back_populates="accesorios")
    fabricante: Mapped[Fabricante] = relationship(back_populates="accesorios")
    items_pedido: Mapped[list[ItemPedido]] = relationship(back_populates="accesorio")
