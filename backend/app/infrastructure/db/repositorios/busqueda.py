from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.catalogo import Busqueda
from app.domain.puertos import RepositorioBusquedas
from app.infrastructure.db.repositorios.conversiones import busqueda_a_dominio, fecha_a_bd
from app.infrastructure.models.busqueda import Busqueda as BusquedaModelo


class RepositorioBusquedasSQLAlchemy(RepositorioBusquedas):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, busqueda: Busqueda) -> Busqueda:
        modelo = BusquedaModelo(
            fecha=fecha_a_bd(busqueda.fecha),
            cuota_maxima_cop=busqueda.cuota_maxima_cop,
            cuota_inicial_cop=busqueda.cuota_inicial_cop,
            categoria_licencia=busqueda.categoria_licencia.value,
            uso=busqueda.uso.value,
            marca_id=busqueda.marca_id,
            cantidad_resultados=busqueda.cantidad_resultados,
        )
        self.sesion.add(modelo)
        self.sesion.flush()
        return busqueda_a_dominio(modelo)

    def listar(self) -> list[Busqueda]:
        consulta = select(BusquedaModelo).order_by(
            BusquedaModelo.fecha.desc(), BusquedaModelo.id.desc()
        )
        return [busqueda_a_dominio(fila) for fila in self.sesion.scalars(consulta).all()]
