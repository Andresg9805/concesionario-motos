from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.atencion import Cotizacion, EstadoAtencion
from app.domain.catalogo import PlanCredito
from app.domain.estados_cotizacion import ESTADOS_CERRADOS
from app.domain.puertos import RepositorioCotizaciones
from app.infrastructure.db.repositorios.conversiones import (
    cliente_a_dominio,
    moto_a_dominio,
    usuario_a_dominio,
)
from app.infrastructure.models.asesor import Asesor as AsesorModelo
from app.infrastructure.models.cotizacion import Cotizacion as CotizacionModelo
from app.infrastructure.models.moto import Moto as MotoModelo
from app.infrastructure.models.persona import Persona as PersonaModelo
from app.infrastructure.models.usuario import Usuario as UsuarioModelo

ESTADOS_CERRADOS_BD = tuple(estado.value for estado in ESTADOS_CERRADOS)


def _a_dominio(modelo: CotizacionModelo) -> Cotizacion:
    return Cotizacion(
        id=modelo.id,
        codigo_seguimiento=modelo.codigo_seguimiento,
        cliente=cliente_a_dominio(modelo.cliente),
        moto=moto_a_dominio(modelo.moto),
        asesor=usuario_a_dominio(modelo.asesor.usuario),
        fecha=modelo.fecha,
        plan=PlanCredito(
            precio_cop=modelo.precio_cop,
            cuota_inicial_cop=modelo.cuota_inicial_cop,
            plazo_meses=modelo.plazo_meses,
            tasa_mensual=float(modelo.tasa_mensual),
        ),
        estado=EstadoAtencion(modelo.estado_atencion),
    )


class RepositorioCotizacionesSQLAlchemy(RepositorioCotizaciones):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, cotizacion: Cotizacion) -> Cotizacion:
        cliente = self.sesion.get(PersonaModelo, cotizacion.cliente.id or 0)
        moto = self.sesion.get(MotoModelo, cotizacion.moto.id or 0)
        asesor = self.sesion.get(AsesorModelo, cotizacion.asesor.id or 0)

        if cliente is None:
            raise ValueError("El cliente indicado no existe en la base de datos")
        if moto is None:
            raise ValueError("La moto indicada no existe en la base de datos")
        if asesor is None:
            raise ValueError("El asesor indicado no existe en la base de datos")

        if cotizacion.id is None:
            modelo = CotizacionModelo()
            self.sesion.add(modelo)
        else:
            existente = self.sesion.get(CotizacionModelo, cotizacion.id)
            if existente is None:
                raise ValueError("La cotización indicada no existe en la base de datos")
            modelo = existente

        modelo.codigo_seguimiento = cotizacion.codigo_seguimiento
        modelo.cliente_id = cliente.id
        modelo.moto_id = moto.id
        modelo.asesor_id = asesor.usuario_id
        modelo.fecha = cotizacion.fecha
        modelo.precio_cop = cotizacion.plan.precio_cop
        modelo.cuota_inicial_cop = cotizacion.plan.cuota_inicial_cop
        modelo.plazo_meses = cotizacion.plan.plazo_meses
        modelo.tasa_mensual = Decimal(str(cotizacion.plan.tasa_mensual))
        modelo.estado_atencion = cotizacion.estado.value

        self.sesion.flush()
        self.sesion.refresh(modelo)
        cotizacion.id = modelo.id
        return _a_dominio(modelo)

    def buscar_por_codigo(self, codigo: str) -> Cotizacion | None:
        modelo = self.sesion.scalar(
            select(CotizacionModelo).where(CotizacionModelo.codigo_seguimiento == codigo)
        )
        return None if modelo is None else _a_dominio(modelo)

    def buscar_por_id(self, id: int) -> Cotizacion | None:
        modelo = self.sesion.get(CotizacionModelo, id)
        return None if modelo is None else _a_dominio(modelo)

    def listar_por_asesor(self, asesor_id: int) -> list[Cotizacion]:
        modelos = self.sesion.scalars(
            select(CotizacionModelo)
            .where(CotizacionModelo.asesor_id == asesor_id)
            .order_by(CotizacionModelo.fecha.desc(), CotizacionModelo.id.desc())
        ).all()
        return [_a_dominio(modelo) for modelo in modelos]

    def listar_por_usuario(self, usuario_id: int) -> list[Cotizacion]:
        modelos = self.sesion.scalars(
            select(CotizacionModelo)
            .join(UsuarioModelo, UsuarioModelo.persona_id == CotizacionModelo.cliente_id)
            .where(UsuarioModelo.id == usuario_id)
            .order_by(CotizacionModelo.fecha.desc(), CotizacionModelo.id.desc())
        ).all()
        return [_a_dominio(modelo) for modelo in modelos]

    def contar_abiertas_por_asesor(self, marca_id: int) -> dict[int, int]:
        filas = self.sesion.execute(
            select(CotizacionModelo.asesor_id, func.count(CotizacionModelo.id))
            .join(CotizacionModelo.asesor)
            .where(
                AsesorModelo.marca_id == marca_id,
                CotizacionModelo.estado_atencion.notin_(ESTADOS_CERRADOS_BD),
            )
            .group_by(CotizacionModelo.asesor_id)
        ).all()
        return {asesor_id: cantidad for asesor_id, cantidad in filas}
