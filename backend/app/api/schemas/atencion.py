from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.api.schemas.auth import PATRON_CELULAR, PATRON_CORREO, EntradaEstricta
from app.api.schemas.motos import PLAZO_MAXIMO_MESES, PLAZO_MINIMO_MESES, MarcaResumenSalida
from app.application.atencion import ZONA_COLOMBIA, Atencion
from app.domain.atencion import Cliente, Cotizacion, EstadoAtencion, EstadoTestDrive, TestDrive
from app.domain.catalogo import Moto

TipoAtencion = Literal["COTIZACION", "TEST_DRIVE"]


class TestDriveEntrada(EntradaEstricta):
    moto_id: int = Field(ge=1, examples=[3])
    nombre: str = Field(min_length=3, max_length=120, examples=["Ana Pérez"])
    correo: str = Field(max_length=254, pattern=PATRON_CORREO, examples=["ana@correo.com"])
    celular: str = Field(pattern=PATRON_CELULAR, examples=["3001234567"])
    acepta_contacto: bool = Field(examples=[True])

    @field_validator("correo")
    @classmethod
    def normalizar_correo(cls, correo: str) -> str:
        return correo.lower()

    @field_validator("acepta_contacto")
    @classmethod
    def exigir_autorizacion(cls, acepta: bool) -> bool:
        if not acepta:
            raise ValueError("Debes autorizar que el asesor te contacte")
        return acepta


class CotizacionEntrada(TestDriveEntrada):
    cuota_inicial_cop: int = Field(default=0, ge=0, le=500_000_000, examples=[1_289_000])
    plazo_meses: int = Field(
        default=36, ge=PLAZO_MINIMO_MESES, le=PLAZO_MAXIMO_MESES, examples=[36]
    )


class CambioEstadoEntrada(EntradaEstricta):
    estado: EstadoAtencion = Field(examples=[EstadoAtencion.CONTACTADO])


class ProgramarTestDriveEntrada(EntradaEstricta):
    fecha: datetime = Field(examples=["2026-11-15T10:00:00"])

    @field_validator("fecha")
    @classmethod
    def usar_hora_colombia(cls, fecha: datetime) -> datetime:
        return fecha if fecha.tzinfo is not None else fecha.replace(tzinfo=ZONA_COLOMBIA)


class MotoAtencionSalida(BaseModel):
    id: int
    modelo: str
    marca: MarcaResumenSalida

    @classmethod
    def desde_dominio(cls, moto: Moto) -> "MotoAtencionSalida":
        return cls(
            id=moto.id or 0, modelo=moto.modelo, marca=MarcaResumenSalida.desde_dominio(moto.marca)
        )


class AsesorAtencionSalida(BaseModel):
    nombre: str
    whatsapp: str


class ContactoClienteSalida(BaseModel):
    nombre: str
    correo: str
    celular: str

    @classmethod
    def desde_dominio(cls, cliente: Cliente) -> "ContactoClienteSalida":
        return cls(nombre=cliente.nombre, correo=cliente.correo, celular=cliente.telefono)


def _como_fecha_hora(fecha: date) -> datetime:
    return fecha if isinstance(fecha, datetime) else datetime.combine(fecha, time())


class AtencionSalida(BaseModel):
    codigo: str
    tipo: TipoAtencion
    estado: EstadoAtencion | EstadoTestDrive
    creada_en: datetime
    moto: MotoAtencionSalida
    asesor: AsesorAtencionSalida
    cuota_mensual_cop: int | None

    @classmethod
    def campos(cls, atencion: Atencion) -> dict[str, object]:
        return {
            "codigo": atencion.codigo_seguimiento,
            "tipo": "COTIZACION" if isinstance(atencion, Cotizacion) else "TEST_DRIVE",
            "estado": atencion.estado,
            "creada_en": _como_fecha_hora(
                atencion.fecha if isinstance(atencion, Cotizacion) else atencion.fecha_solicitud
            ),
            "moto": MotoAtencionSalida.desde_dominio(atencion.moto),
            "asesor": AsesorAtencionSalida(
                nombre=atencion.asesor.nombre, whatsapp=atencion.asesor.telefono
            ),
            "cuota_mensual_cop": (
                atencion.cuota_mensual() if isinstance(atencion, Cotizacion) else None
            ),
        }

    @classmethod
    def desde_dominio(cls, atencion: Atencion) -> "AtencionSalida":
        return cls.model_validate(cls.campos(atencion))


class AtencionAsesorSalida(AtencionSalida):
    id: int
    cliente: ContactoClienteSalida
    fecha_programada: datetime | None = None

    @classmethod
    def desde_dominio(cls, atencion: Atencion) -> "AtencionAsesorSalida":
        return cls.model_validate(
            {
                **cls.campos(atencion),
                "id": atencion.id or 0,
                "cliente": ContactoClienteSalida.desde_dominio(atencion.cliente),
                "fecha_programada": (
                    atencion.fecha_programada if isinstance(atencion, TestDrive) else None
                ),
            }
        )
