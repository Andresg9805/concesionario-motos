
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.atencion import (
    Cliente,
    Cotizacion,
    EstadoAtencion,
    Rol,
    Usuario,
)
from app.domain.catalogo import (
    CategoriaLicencia,
    Marca,
    Moto,
    PlanCredito,
    TipoMoto,
)
from app.domain.puertos import RepositorioCotizaciones
from app.infrastructure.models.cliente import Cliente as ClienteModelo
from app.infrastructure.models.cotizacion import Cotizacion as CotizacionModelo
from app.infrastructure.models.marca import Marca as MarcaModelo
from app.infrastructure.models.moto import Moto as MotoModelo
from app.infrastructure.models.usuario import Usuario as UsuarioModelo


class RepositorioCotizacionesSQLAlchemy(RepositorioCotizaciones):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    @staticmethod
    def _marca_a_dominio(marca: MarcaModelo) -> Marca:
        return Marca(
            id=marca.id,
            nombre=marca.nombre,
            color_hex=marca.color_hex,
            descripcion=marca.descripcion,
        )

    @classmethod
    def _usuario_a_dominio(cls, usuario: UsuarioModelo) -> Usuario:
        marca_especialidad = None

        if usuario.marca_especialidad is not None:
            marca_especialidad = cls._marca_a_dominio(
                usuario.marca_especialidad
            )

        return Usuario(
            id=usuario.id,
            nombre=usuario.nombre,
            correo=usuario.correo,
            telefono=usuario.telefono,
            hash_contrasena=usuario.hash_contrasena,
            rol=Rol(usuario.rol),
            marca_especialidad=marca_especialidad,
        )

    @classmethod
    def _cliente_a_dominio(cls, cliente: ClienteModelo) -> Cliente:
        usuario = None

        if cliente.usuario is not None:
            usuario = cls._usuario_a_dominio(cliente.usuario)

        return Cliente(
            id=cliente.id,
            nombre=cliente.nombre,
            correo=cliente.correo,
            telefono=cliente.telefono,
            usuario=usuario,
        )

    @classmethod
    def _moto_a_dominio(cls, moto: MotoModelo) -> Moto:
        return Moto(
            id=moto.id,
            marca=cls._marca_a_dominio(moto.marca),
            modelo=moto.modelo,
            anio=moto.anio,
            cilindraje_cc=moto.cilindraje_cc,
            tipo=TipoMoto(moto.tipo),
            categoria_licencia=CategoriaLicencia(
                moto.categoria_licencia
            ),
            precio_cop=moto.precio_cop,
            stock=moto.stock,
            consumo_km_galon=moto.consumo_km_galon,
            costo_mantenimiento_km_cop=moto.costo_mantenimiento_km_cop,
            descripcion=moto.descripcion,
            imagen_url=moto.imagen_url,
        )

    @classmethod
    def _a_dominio(
        cls,
        cotizacion: CotizacionModelo,
    ) -> Cotizacion:
        plan = PlanCredito(
            precio_cop=cotizacion.precio_cop,
            cuota_inicial_cop=cotizacion.cuota_inicial_cop,
            plazo_meses=cotizacion.plazo_meses,
            tasa_mensual=float(cotizacion.tasa_mensual),
        )

        return Cotizacion(
            id=cotizacion.id,
            codigo_seguimiento=cotizacion.codigo_seguimiento,
            cliente=cls._cliente_a_dominio(cotizacion.cliente),
            moto=cls._moto_a_dominio(cotizacion.moto),
            asesor=cls._usuario_a_dominio(cotizacion.asesor),
            fecha=cotizacion.fecha,
            plan=plan,
            estado=EstadoAtencion(cotizacion.estado_atencion),
        )

    def guardar(self, cotizacion: Cotizacion) -> Cotizacion:
        if cotizacion.cliente.id is None:
            raise ValueError("El cliente debe estar guardado en la base de datos")

        if cotizacion.moto.id is None:
            raise ValueError("La moto debe estar guardada en la base de datos")

        if cotizacion.asesor.id is None:
            raise ValueError("El asesor debe estar guardado en la base de datos")

        cliente = self.sesion.get(ClienteModelo, cotizacion.cliente.id)
        moto = self.sesion.get(MotoModelo, cotizacion.moto.id)
        asesor = self.sesion.get(UsuarioModelo, cotizacion.asesor.id)

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
            modelo = self.sesion.get(CotizacionModelo, cotizacion.id)

            if modelo is None:
                raise ValueError(
                    "La cotización indicada no existe en la base de datos"
                )

        modelo.codigo_seguimiento = cotizacion.codigo_seguimiento
        modelo.cliente_id = cliente.id
        modelo.moto_id = moto.id
        modelo.asesor_id = asesor.id
        modelo.fecha = cotizacion.fecha
        modelo.precio_cop = cotizacion.plan.precio_cop
        modelo.cuota_inicial_cop = cotizacion.plan.cuota_inicial_cop
        modelo.plazo_meses = cotizacion.plan.plazo_meses
        modelo.tasa_mensual = cotizacion.plan.tasa_mensual
        modelo.cuota_mensual_cop = cotizacion.cuota_mensual()
        modelo.estado_atencion = cotizacion.estado.value

        self.sesion.flush()

        cotizacion.id = modelo.id

        return self._a_dominio(modelo)

    def buscar_por_codigo(self, codigo: str) -> Cotizacion | None:
        consulta = select(CotizacionModelo).where(
            CotizacionModelo.codigo_seguimiento == codigo
        )

        resultado = self.sesion.execute(consulta).scalar_one_or_none()

        if resultado is None:
            return None

        return self._a_dominio(resultado)

    def buscar_por_id(self, id: int) -> Cotizacion | None:
        resultado = self.sesion.get(CotizacionModelo, id)

        if resultado is None:
            return None

        return self._a_dominio(resultado)

    def listar_por_asesor(self, asesor_id: int) -> list[Cotizacion]:
        consulta = (
            select(CotizacionModelo)
            .where(CotizacionModelo.asesor_id == asesor_id)
            .order_by(CotizacionModelo.fecha.desc())
        )

        resultados = self.sesion.execute(consulta).scalars().all()

        return [self._a_dominio(resultado) for resultado in resultados]

    def listar_por_usuario(self, usuario_id: int) -> list[Cotizacion]:
        consulta = (
            select(CotizacionModelo)
            .join(
                ClienteModelo,
                CotizacionModelo.cliente_id == ClienteModelo.id,
            )
            .where(ClienteModelo.usuario_id == usuario_id)
            .order_by(CotizacionModelo.fecha.desc())
        )

        resultados = self.sesion.execute(consulta).scalars().all()

        return [self._a_dominio(resultado) for resultado in resultados]

    def contar_abiertas_por_asesor(
        self,
        marca_id: int,
    ) -> dict[int, int]:
        consulta = (
            select(
                CotizacionModelo.asesor_id,
                func.count(CotizacionModelo.id),
            )
            .join(
                MotoModelo,
                CotizacionModelo.moto_id == MotoModelo.id,
            )
            .where(
                MotoModelo.marca_id == marca_id,
                CotizacionModelo.estado_atencion.notin_(
                    [
                        EstadoAtencion.VENDIDO.value,
                        EstadoAtencion.DESCARTADO.value,
                    ]
                ),
            )
            .group_by(CotizacionModelo.asesor_id)
        )

        resultados = self.sesion.execute(consulta).all()

        return {
            asesor_id: cantidad
            for asesor_id, cantidad in resultados
        }
