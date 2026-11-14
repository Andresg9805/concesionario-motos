from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.cliente import Cliente
    from app.infrastructure.models.cotizacion import Cotizacion
    from app.infrastructure.models.direccion import Direccion
    from app.infrastructure.models.marca import Marca
    from app.infrastructure.models.pedido import Pedido
    from app.infrastructure.models.test_drive import TestDrive


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    nombre: Mapped[str] = mapped_column(String, nullable=False)
    correo: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    telefono: Mapped[str] = mapped_column(String, nullable=False)
    hash_contrasena: Mapped[str] = mapped_column(String, nullable=False)

    rol: Mapped[str] = mapped_column(
        Enum("CLIENTE", "ASESOR", "ADMIN", name="rol_usuario"), nullable=False
    )

    marca_especialidad_id: Mapped[int | None] = mapped_column(
        ForeignKey("marcas.id"), nullable=True
    )

    marca_especialidad: Mapped[Marca | None] = relationship(back_populates="usuarios_especialidad")

    cotizaciones: Mapped[list[Cotizacion]] = relationship(back_populates="asesor")

    test_drives: Mapped[list[TestDrive]] = relationship(back_populates="asesor")

    cliente: Mapped[Cliente | None] = relationship(back_populates="usuario")

    direcciones: Mapped[list[Direccion]] = relationship(back_populates="usuario")

    pedidos: Mapped[list[Pedido]] = relationship(back_populates="usuario")
