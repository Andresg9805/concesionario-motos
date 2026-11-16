from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.asesor import Asesor
    from app.infrastructure.models.direccion import Direccion
    from app.infrastructure.models.pedido import Pedido
    from app.infrastructure.models.persona import Persona


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), unique=True, nullable=False)
    hash_contrasena: Mapped[str] = mapped_column(String, nullable=False)
    rol: Mapped[str] = mapped_column(
        Enum("CLIENTE", "ASESOR", "ADMIN", name="rol_usuario"), nullable=False
    )

    persona: Mapped[Persona] = relationship(back_populates="usuario")
    asesor: Mapped[Asesor | None] = relationship(back_populates="usuario", uselist=False)
    direcciones: Mapped[list[Direccion]] = relationship(back_populates="usuario")
    pedidos: Mapped[list[Pedido]] = relationship(back_populates="usuario")
