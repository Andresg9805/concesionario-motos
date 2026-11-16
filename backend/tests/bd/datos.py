from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.asesor import Asesor
from app.infrastructure.models.marca import Marca
from app.infrastructure.models.moto import Moto
from app.infrastructure.models.persona import Persona
from app.infrastructure.models.tipo_moto import TipoMoto
from app.infrastructure.models.usuario import Usuario


def crear_marca(sesion: Session, nombre: str, color_hex: str = "#CC0000") -> Marca:
    marca = Marca(nombre=nombre, color_hex=color_hex, descripcion=f"Motocicletas {nombre}")
    sesion.add(marca)
    sesion.flush()
    return marca


def crear_moto(
    sesion: Session,
    marca: Marca,
    modelo: str = "CB 190R",
    cilindraje_cc: int = 184,
    precio_cop: int = 12_000_000,
    tipo: str = "NAKED",
) -> Moto:
    tipo_moto = sesion.scalar(select(TipoMoto).where(TipoMoto.clave == tipo))
    assert tipo_moto is not None
    moto = Moto(
        marca_id=marca.id,
        tipo_id=tipo_moto.id,
        modelo=modelo,
        anio=2026,
        cilindraje_cc=cilindraje_cc,
        precio_cop=precio_cop,
        stock=5,
        consumo_km_galon=120.0,
        costo_mantenimiento_km_cop=50,
        descripcion="Moto urbana",
        imagen_url="https://ejemplo.com/moto.jpg",
    )
    sesion.add(moto)
    sesion.flush()
    return moto


def crear_persona(sesion: Session, nombre: str, correo: str, telefono: str) -> Persona:
    persona = Persona(nombre=nombre, correo=correo, telefono=telefono)
    sesion.add(persona)
    sesion.flush()
    return persona


def crear_usuario(
    sesion: Session,
    nombre: str,
    correo: str,
    telefono: str,
    rol: str,
    marca: Marca | None = None,
) -> Usuario:
    persona = crear_persona(sesion, nombre, correo, telefono)
    usuario = Usuario(persona_id=persona.id, hash_contrasena="hash", rol=rol)
    sesion.add(usuario)
    sesion.flush()
    if marca is not None:
        sesion.add(Asesor(usuario_id=usuario.id, marca_id=marca.id))
        sesion.flush()
    return usuario
