from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.domain.atencion import (
    Cliente,
    Cotizacion,
    EstadoAtencion,
    TestDrive,
    Usuario,
    validar_codigo,
)
from app.domain.catalogo import Moto, PlanCredito
from app.domain.excepciones import EntidadNoEncontradaError, PermisoDenegadoError
from app.domain.puertos import (
    RepositorioClientes,
    RepositorioCotizaciones,
    RepositorioMotos,
    RepositorioParametros,
    RepositorioTestDrives,
    RepositorioUsuarios,
)
from app.domain.servicios import AsignadorAsesor, GeneradorCodigo

ZONA_COLOMBIA = timezone(timedelta(hours=-5), "COT")
INTENTOS_CODIGO = 20

Reloj = Callable[[], datetime]
Atencion = Cotizacion | TestDrive


def reloj_colombia() -> datetime:
    return datetime.now(ZONA_COLOMBIA).replace(microsecond=0)


@dataclass(frozen=True)
class DatosContacto:
    nombre: str
    correo: str
    celular: str


class AsignacionAtencion:
    def __init__(
        self,
        motos: RepositorioMotos,
        clientes: RepositorioClientes,
        usuarios: RepositorioUsuarios,
        cotizaciones: RepositorioCotizaciones,
        test_drives: RepositorioTestDrives,
        asignador: AsignadorAsesor | None = None,
        generador: Callable[[], str] = GeneradorCodigo.nuevo_codigo,
    ) -> None:
        self._motos = motos
        self._clientes = clientes
        self._usuarios = usuarios
        self._cotizaciones = cotizaciones
        self._test_drives = test_drives
        self._asignador = asignador or AsignadorAsesor()
        self._generador = generador

    def moto(self, moto_id: int) -> Moto:
        moto = self._motos.buscar_por_id(moto_id)
        if moto is None:
            raise EntidadNoEncontradaError(f"No existe una moto con id {moto_id}")
        return moto

    def cliente(self, contacto: DatosContacto) -> Cliente:
        existente = self._clientes.buscar_por_correo(contacto.correo)
        if existente is not None:
            return existente
        return self._clientes.guardar(
            Cliente(
                nombre=contacto.nombre.strip(),
                correo=contacto.correo,
                telefono=contacto.celular,
            )
        )

    def asesor(self, moto: Moto) -> Usuario:
        marca_id = moto.marca.id or 0
        abiertas = self._cotizaciones.contar_abiertas_por_asesor(marca_id)
        for asesor_id, cantidad in self._test_drives.contar_abiertos_por_asesor(marca_id).items():
            abiertas[asesor_id] = abiertas.get(asesor_id, 0) + cantidad
        return self._asignador.elegir(self._usuarios.listar_asesores(marca_id), abiertas)

    def codigo(self) -> str:
        for _ in range(INTENTOS_CODIGO):
            codigo = self._generador()
            if (
                self._cotizaciones.buscar_por_codigo(codigo) is None
                and self._test_drives.buscar_por_codigo(codigo) is None
            ):
                return codigo
        raise RuntimeError("No se pudo generar un código de seguimiento único")


class SolicitarCotizacion:
    def __init__(
        self,
        asignacion: AsignacionAtencion,
        cotizaciones: RepositorioCotizaciones,
        parametros: RepositorioParametros,
        reloj: Reloj = reloj_colombia,
    ) -> None:
        self._asignacion = asignacion
        self._cotizaciones = cotizaciones
        self._parametros = parametros
        self._reloj = reloj

    def ejecutar(
        self, moto_id: int, contacto: DatosContacto, cuota_inicial_cop: int, plazo_meses: int
    ) -> Cotizacion:
        moto = self._asignacion.moto(moto_id)
        plan = PlanCredito(
            precio_cop=moto.precio_cop,
            cuota_inicial_cop=cuota_inicial_cop,
            plazo_meses=plazo_meses,
            tasa_mensual=self._parametros.obtener().tasa_mensual,
        )
        asesor = self._asignacion.asesor(moto)
        return self._cotizaciones.guardar(
            Cotizacion(
                codigo_seguimiento=self._asignacion.codigo(),
                cliente=self._asignacion.cliente(contacto),
                moto=moto,
                asesor=asesor,
                fecha=self._reloj(),
                plan=plan,
            )
        )


class SolicitarTestDrive:
    def __init__(
        self,
        asignacion: AsignacionAtencion,
        test_drives: RepositorioTestDrives,
        reloj: Reloj = reloj_colombia,
    ) -> None:
        self._asignacion = asignacion
        self._test_drives = test_drives
        self._reloj = reloj

    def ejecutar(self, moto_id: int, contacto: DatosContacto) -> TestDrive:
        moto = self._asignacion.moto(moto_id)
        asesor = self._asignacion.asesor(moto)
        return self._test_drives.guardar(
            TestDrive(
                codigo_seguimiento=self._asignacion.codigo(),
                cliente=self._asignacion.cliente(contacto),
                moto=moto,
                asesor=asesor,
                fecha_solicitud=self._reloj(),
            )
        )


class ConsultarSeguimiento:
    def __init__(
        self, cotizaciones: RepositorioCotizaciones, test_drives: RepositorioTestDrives
    ) -> None:
        self._cotizaciones = cotizaciones
        self._test_drives = test_drives

    def ejecutar(self, codigo: str) -> Atencion:
        limpio = codigo.strip().upper()
        no_existe = EntidadNoEncontradaError(f"No hay ninguna atención con el código {limpio}")
        try:
            validar_codigo(limpio)
        except ValueError as error:
            raise no_existe from error
        atencion: Atencion | None = self._cotizaciones.buscar_por_codigo(limpio)
        if atencion is None:
            atencion = self._test_drives.buscar_por_codigo(limpio)
        if atencion is None:
            raise no_existe
        return atencion


class ListarAtencionesAsesor:
    def __init__(self, cotizaciones: RepositorioCotizaciones) -> None:
        self._cotizaciones = cotizaciones

    def ejecutar(self, asesor_id: int) -> list[Cotizacion]:
        return self._cotizaciones.listar_por_asesor(asesor_id)


class CambiarEstadoCotizacion:
    def __init__(self, cotizaciones: RepositorioCotizaciones) -> None:
        self._cotizaciones = cotizaciones

    def ejecutar(self, asesor_id: int, cotizacion_id: int, estado: EstadoAtencion) -> Cotizacion:
        cotizacion = self._cotizaciones.buscar_por_id(cotizacion_id)
        if cotizacion is None:
            raise EntidadNoEncontradaError(f"No existe una cotización con id {cotizacion_id}")
        if cotizacion.asesor.id != asesor_id:
            raise PermisoDenegadoError("Esta cotización la atiende otro asesor")
        cotizacion.cambiar_estado(estado)
        return self._cotizaciones.guardar(cotizacion)


class ListarColaTestDrives:
    def __init__(self, test_drives: RepositorioTestDrives) -> None:
        self._test_drives = test_drives

    def ejecutar(self, asesor_id: int) -> list[TestDrive]:
        return self._test_drives.listar_pendientes(asesor_id)


class AtenderSiguienteTestDrive:
    def __init__(self, test_drives: RepositorioTestDrives) -> None:
        self._test_drives = test_drives

    def ejecutar(self, asesor_id: int, fecha: datetime) -> TestDrive:
        cola = self._test_drives.listar_pendientes(asesor_id)
        if not cola:
            raise EntidadNoEncontradaError("No tienes test drives pendientes")
        siguiente = cola[0]
        siguiente.programar(fecha)
        return self._test_drives.guardar(siguiente)
