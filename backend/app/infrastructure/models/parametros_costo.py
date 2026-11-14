from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class ParametrosCosto(Base):
    __tablename__ = "parametros_costo"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    precio_galon_cop: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    porcentaje_impuesto: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )

    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )
