import re
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from app.domain.catalogo import Marca, Moto, PlanCredito
from app.domain.excepciones import TestDriveInvalidoError, TransicionInvalidaError

PATRON_CODIGO = re.compile(r"^CM-[A-Z0-9]{4}$")


def validar_codigo(codigo: str) -> None:
    if not PATRON_CODIGO.match(codigo):
        raise ValueError(f"El código {codigo} no tiene el formato CM-XXXX")


class Rol(StrEnum):
    CLIENTE = "CLIENTE"
    ASESOR = "ASESOR"
    ADMIN = "ADMIN"


class EstadoAtencion(StrEnum):
    NUEVO = "NUEVO"
    CONTACTADO = "CONTACTADO"
    TEST_DRIVE = "TEST_DRIVE"
    NEGOCIANDO = "NEGOCIANDO"
    VENDIDO = "VENDIDO"
    DESCARTADO = "DESCARTADO"


TRANSICIONES_ATENCION: dict[EstadoAtencion, set[EstadoAtencion]] = {
    EstadoAtencion.NUEVO: {EstadoAtencion.CONTACTADO, EstadoAtencion.DESCARTADO},
    EstadoAtencion.CONTACTADO: {
        EstadoAtencion.TEST_DRIVE,
        EstadoAtencion.NEGOCIANDO,
        EstadoAtencion.DESCARTADO,
    },
    EstadoAtencion.TEST_DRIVE: {EstadoAtencion.NEGOCIANDO, EstadoAtencion.DESCARTADO},
    EstadoAtencion.NEGOCIANDO: {EstadoAtencion.VENDIDO, EstadoAtencion.DESCARTADO},
    EstadoAtencion.VENDIDO: set(),
    EstadoAtencion.DESCARTADO: set(),
}


class EstadoTestDrive(StrEnum):
    PENDIENTE = "PENDIENTE"
    PROGRAMADO = "PROGRAMADO"
    REALIZADO = "REALIZADO"
    CANCELADO = "CANCELADO"


@dataclass(kw_only=True)
class Usuario:
    id: int | None = None
    nombre: str
    correo: str
    telefono: str = ""
    hash_contrasena: str
    rol: Rol
    marca_especialidad: Marca | None = None

    def __post_init__(self) -> None:
        self.correo = self.correo.strip().lower()
        if "@" not in self.correo:
            raise ValueError("El correo no es válido")
        if self.rol == Rol.ASESOR and self.marca_especialidad is None:
            raise ValueError("Un asesor debe tener una marca de especialidad")
        if self.rol != Rol.ASESOR and self.marca_especialidad is not None:
            raise ValueError("Solo los asesores tienen marca de especialidad")

    def es_admin(self) -> bool:
        return self.rol == Rol.ADMIN

    def es_asesor(self) -> bool:
        return self.rol == Rol.ASESOR

    def enlace_whatsapp(self) -> str:
        numero = re.sub(r"\D", "", self.telefono)
        if not numero:
            return ""
        if not numero.startswith("57"):
            numero = "57" + numero
        return f"https://wa.me/{numero}"


@dataclass(kw_only=True)
class Cliente:
    id: int | None = None
    nombre: str
    correo: str
    telefono: str
    usuario: Usuario | None = None

    def __post_init__(self) -> None:
        self.correo = self.correo.strip().lower()
        if "@" not in self.correo:
            raise ValueError("El correo no es válido")


def _validar_asesor(asesor: Usuario, moto: Moto) -> None:
    if not asesor.es_asesor():
        raise ValueError("La atención debe tener un asesor")
    if asesor.marca_especialidad is None or asesor.marca_especialidad.nombre != moto.marca.nombre:
        raise ValueError("El asesor debe ser especialista en la marca de la moto")


@dataclass(kw_only=True)
class Cotizacion:
    id: int | None = None
    codigo_seguimiento: str
    cliente: Cliente
    moto: Moto
    asesor: Usuario
    fecha: date
    plan: PlanCredito
    estado: EstadoAtencion = EstadoAtencion.NUEVO

    def __post_init__(self) -> None:
        validar_codigo(self.codigo_seguimiento)
        _validar_asesor(self.asesor, self.moto)
        if self.plan.precio_cop != self.moto.precio_cop:
            raise ValueError("El plan de crédito debe usar el precio de la moto")

    def cuota_mensual(self) -> int:
        return self.plan.cuota_mensual()

    def esta_abierta(self) -> bool:
        return self.estado not in (EstadoAtencion.VENDIDO, EstadoAtencion.DESCARTADO)

    def cambiar_estado(self, nuevo: EstadoAtencion) -> None:
        if nuevo not in TRANSICIONES_ATENCION[self.estado]:
            raise TransicionInvalidaError(
                f"No se puede pasar de {self.estado.value} a {nuevo.value}"
            )
        self.estado = nuevo


@dataclass(kw_only=True)
class TestDrive:
    id: int | None = None
    codigo_seguimiento: str
    cliente: Cliente
    moto: Moto
    asesor: Usuario
    fecha_solicitud: datetime
    fecha_programada: datetime | None = None
    estado: EstadoTestDrive = EstadoTestDrive.PENDIENTE

    def __post_init__(self) -> None:
        validar_codigo(self.codigo_seguimiento)
        _validar_asesor(self.asesor, self.moto)

    def programar(self, fecha: datetime) -> None:
        if self.estado not in (EstadoTestDrive.PENDIENTE, EstadoTestDrive.PROGRAMADO):
            raise TransicionInvalidaError(
                f"No se puede programar un test drive {self.estado.value}"
            )
        if fecha <= self.fecha_solicitud:
            raise TestDriveInvalidoError("La fecha debe ser posterior a la solicitud")
        self.fecha_programada = fecha
        self.estado = EstadoTestDrive.PROGRAMADO

    def marcar_realizado(self) -> None:
        if self.estado != EstadoTestDrive.PROGRAMADO:
            raise TransicionInvalidaError("Solo se puede realizar un test drive programado")
        self.estado = EstadoTestDrive.REALIZADO

    def cancelar(self) -> None:
        if self.estado not in (EstadoTestDrive.PENDIENTE, EstadoTestDrive.PROGRAMADO):
            raise TransicionInvalidaError(f"No se puede cancelar un test drive {self.estado.value}")
        self.estado = EstadoTestDrive.CANCELADO
