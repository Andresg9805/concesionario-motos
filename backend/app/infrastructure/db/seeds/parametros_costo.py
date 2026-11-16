
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.parametros_costo import ParametrosCosto
from app.infrastructure.models.tarifa_soat import TarifaSoat


def seed_parametros_costo(db: Session) -> None:
    parametros = db.scalar(
        select(ParametrosCosto).where(ParametrosCosto.id == 1)
    )

    if parametros is None:
        parametros = ParametrosCosto(
            id=1,
            precio_galon_cop=16_200,
            porcentaje_impuesto=Decimal("1.50"),
            actualizado_en=datetime.now(),
        )
        db.add(parametros)
    else:
        parametros.precio_galon_cop = 16_200
        parametros.porcentaje_impuesto = Decimal("1.50")
        parametros.actualizado_en = datetime.now()

    tarifas = [
        (0, 99, 256_000),
        (100, 200, 343_000),
        (201, 100_000, 790_000),
    ]

    for cilindraje_min, cilindraje_max, valor_anual_cop in tarifas:
        tarifa = db.scalar(
            select(TarifaSoat).where(
                TarifaSoat.cilindraje_min == cilindraje_min,
                TarifaSoat.cilindraje_max == cilindraje_max,
            )
        )

        if tarifa is None:
            tarifa = TarifaSoat(
                cilindraje_min=cilindraje_min,
                cilindraje_max=cilindraje_max,
                valor_anual_cop=valor_anual_cop,
            )
            db.add(tarifa)
        else:
            tarifa.valor_anual_cop = valor_anual_cop
