
from sqlalchemy import Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class TarifaSoat(Base):
    __tablename__ = "tarifas_soat"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    cilindraje_min: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    cilindraje_max: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    valor_anual_cop: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
