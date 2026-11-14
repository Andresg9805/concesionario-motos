from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CHAR, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.municipio import Municipio
    from app.infrastructure.models.pedido import Pedido
    from app.infrastructure.models.usuario import Usuario


class Direccion(Base):
    __tablename__ = "direcciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    municipio_codigo: Mapped[str] = mapped_column(
        CHAR(5),
        ForeignKey("municipios.codigo", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )

    telefono_contacto: Mapped[str] = mapped_column(String(20), nullable=False)

    detalle: Mapped[str] = mapped_column(Text, nullable=False)

    municipio: Mapped[Municipio] = relationship(back_populates="direcciones")

    usuario: Mapped[Usuario] = relationship(back_populates="direcciones")

    pedidos: Mapped[list[Pedido]] = relationship(back_populates="direccion")
