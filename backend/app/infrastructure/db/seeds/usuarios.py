import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.memoria.datos_prueba import ASESORES
from app.infrastructure.models.asesor import Asesor
from app.infrastructure.models.marca import Marca
from app.infrastructure.models.persona import Persona
from app.infrastructure.models.usuario import Usuario
from app.infrastructure.seguridad.bcrypt_hasheador import HasheadorBcrypt


def _crear_usuario(
    db: Session,
    nombre: str,
    correo: str,
    telefono: str,
    contrasena: str,
    rol: str,
) -> Usuario:
    persona = db.scalar(select(Persona).where(Persona.correo == correo))

    if persona is None:
        persona = Persona(
            nombre=nombre,
            correo=correo,
            telefono=telefono,
        )
        db.add(persona)
        db.flush()

    usuario = db.scalar(
        select(Usuario).where(Usuario.persona_id == persona.id)
    )

    if usuario is None:
        usuario = Usuario(
            persona_id=persona.id,
            hash_contrasena=HasheadorBcrypt().hashear(contrasena),
            rol=rol,
        )
        db.add(usuario)
        db.flush()

    return usuario


def seed_usuarios(db: Session) -> None:
    contrasena_asesores = os.environ.get("CONTRASENA_ASESORES_DEMO")
    contrasena_admin = os.environ.get("CONTRASENA_ADMIN_DEMO")

    if not contrasena_asesores:
        raise ValueError("Falta configurar CONTRASENA_ASESORES_DEMO.")

    if not contrasena_admin:
        raise ValueError("Falta configurar CONTRASENA_ADMIN_DEMO.")

    for marca_id, nombre, correo, telefono in ASESORES:
        usuario = _crear_usuario(
            db=db,
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            contrasena=contrasena_asesores,
            rol="ASESOR",
        )

        asesor = db.get(Asesor, usuario.id)

        if asesor is None:
            marca = db.get(Marca, marca_id)

            if marca is None:
                raise ValueError(f"No existe la marca con ID {marca_id}.")

            db.add(
                Asesor(
                    usuario_id=usuario.id,
                    marca_id=marca.id,
                )
            )

    _crear_usuario(
        db=db,
        nombre="Administrador Candela",
        correo="admin@candela.com",
        telefono="3000000000",
        contrasena=contrasena_admin,
        rol="ADMIN",
    )

    _crear_usuario(
        db=db,
        nombre="Cliente de Prueba",
        correo="cliente.prueba@candela.com",
        telefono="3000000001",
        contrasena=contrasena_asesores,
        rol="CLIENTE",
    )
