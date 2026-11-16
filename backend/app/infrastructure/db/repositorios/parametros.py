from datetime import datetime
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.domain.costo_real import ParametrosCosto
from app.domain.puertos import RepositorioParametros
from app.infrastructure.db.repositorios.conversiones import ZONA_COLOMBIA, parametros_a_dominio
from app.infrastructure.models.parametros_costo import ParametrosCosto as ParametrosModelo
from app.infrastructure.models.tarifa_soat import TarifaSoat as TarifaSoatModelo


class RepositorioParametrosSQLAlchemy(RepositorioParametros):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def _fila(self) -> ParametrosModelo | None:
        return self.sesion.scalars(select(ParametrosModelo).order_by(ParametrosModelo.id)).first()

    def _tarifas(self) -> list[TarifaSoatModelo]:
        consulta = select(TarifaSoatModelo).order_by(TarifaSoatModelo.cilindraje_min)
        return list(self.sesion.scalars(consulta).all())

    def obtener(self) -> ParametrosCosto:
        fila = self._fila()
        if fila is None:
            raise LookupError("No hay parámetros de costo en la base de datos")
        return parametros_a_dominio(fila, self._tarifas())

    def guardar(self, parametros: ParametrosCosto) -> ParametrosCosto:
        fila = self._fila()
        if fila is None:
            fila = ParametrosModelo()
            self.sesion.add(fila)
        fila.precio_galon_cop = parametros.precio_galon_cop
        fila.porcentaje_impuesto = Decimal(str(parametros.porcentaje_impuesto))
        fila.valor_matricula_cop = parametros.valor_matricula_cop
        fila.valor_tramites_cop = parametros.valor_tramites_cop
        fila.tasa_mensual = Decimal(str(parametros.tasa_mensual))
        fila.actualizado_en = datetime.now(ZONA_COLOMBIA).replace(tzinfo=None)
        self.sesion.execute(delete(TarifaSoatModelo))
        for tarifa in parametros.tarifas_soat:
            self.sesion.add(
                TarifaSoatModelo(
                    cilindraje_min=tarifa.cilindraje_min,
                    cilindraje_max=tarifa.cilindraje_max,
                    valor_anual_cop=tarifa.valor_anual_cop,
                )
            )
        self.sesion.flush()
        return self.obtener()
