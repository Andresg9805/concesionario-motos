from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.memoria.datos_prueba import parametros_iniciales
from app.infrastructure.models.parametros_costo import ParametrosCosto
from app.infrastructure.models.tarifa_soat import TarifaSoat


def seed_parametros_costo(db: Session) -> None:
    iniciales = parametros_iniciales()

    if db.scalar(select(ParametrosCosto)) is None:
        db.add(
            ParametrosCosto(
                precio_galon_cop=iniciales.precio_galon_cop,
                porcentaje_impuesto=Decimal(str(iniciales.porcentaje_impuesto)),
                valor_matricula_cop=iniciales.valor_matricula_cop,
                valor_tramites_cop=iniciales.valor_tramites_cop,
                tasa_mensual=Decimal(str(iniciales.tasa_mensual)),
                actualizado_en=datetime.now(),
            )
        )

    if db.scalar(select(TarifaSoat)) is None:
        for tarifa in iniciales.tarifas_soat:
            db.add(
                TarifaSoat(
                    cilindraje_min=tarifa.cilindraje_min,
                    cilindraje_max=tarifa.cilindraje_max,
                    valor_anual_cop=tarifa.valor_anual_cop,
                )
            )
