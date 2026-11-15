from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.atencion import Cliente, Rol, Usuario
from app.domain.puertos import RepositorioClientes, RepositorioUsuarios
from app.infrastructure.db.repositorios.conversiones import cliente_a_dominio, usuario_a_dominio
from app.infrastructure.models.asesor import Asesor as AsesorModelo
from app.infrastructure.models.persona import Persona as PersonaModelo
from app.infrastructure.models.usuario import Usuario as UsuarioModelo


def _persona_por_correo(sesion: Session, correo: str) -> PersonaModelo | None:
    return sesion.scalar(select(PersonaModelo).where(PersonaModelo.correo == correo))


class RepositorioClientesSQLAlchemy(RepositorioClientes):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, cliente: Cliente) -> Cliente:
        persona = _persona_por_correo(self.sesion, cliente.correo)
        if persona is None:
            persona = PersonaModelo(correo=cliente.correo)
            self.sesion.add(persona)
        persona.nombre = cliente.nombre
        persona.telefono = cliente.telefono
        self.sesion.flush()
        self.sesion.refresh(persona)
        return cliente_a_dominio(persona)

    def buscar_por_correo(self, correo: str) -> Cliente | None:
        persona = _persona_por_correo(self.sesion, correo.strip().lower())
        return None if persona is None else cliente_a_dominio(persona)


class RepositorioUsuariosSQLAlchemy(RepositorioUsuarios):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, usuario: Usuario) -> Usuario:
        modelo = self.sesion.get(UsuarioModelo, usuario.id) if usuario.id else None
        persona = _persona_por_correo(self.sesion, usuario.correo)

        if persona is not None and persona.usuario is not None and persona.usuario is not modelo:
            raise ValueError("Ya existe un usuario con ese correo")

        if modelo is None:
            if persona is None:
                persona = PersonaModelo(correo=usuario.correo)
                self.sesion.add(persona)
            modelo = UsuarioModelo(persona=persona)
            self.sesion.add(modelo)
        elif persona is None:
            modelo.persona.correo = usuario.correo

        modelo.persona.nombre = usuario.nombre
        modelo.persona.telefono = usuario.telefono
        modelo.hash_contrasena = usuario.hash_contrasena
        modelo.rol = usuario.rol.value
        self.sesion.flush()

        if usuario.rol == Rol.ASESOR and usuario.marca_especialidad is not None:
            if modelo.asesor is None:
                modelo.asesor = AsesorModelo(usuario_id=modelo.id)
            modelo.asesor.marca_id = usuario.marca_especialidad.id or 0
        elif modelo.asesor is not None:
            self.sesion.delete(modelo.asesor)

        self.sesion.flush()
        self.sesion.refresh(modelo)
        return usuario_a_dominio(modelo)

    def buscar_por_correo(self, correo: str) -> Usuario | None:
        persona = _persona_por_correo(self.sesion, correo.strip().lower())
        if persona is None or persona.usuario is None:
            return None
        return usuario_a_dominio(persona.usuario)

    def buscar_por_id(self, id: int) -> Usuario | None:
        usuario = self.sesion.get(UsuarioModelo, id)
        return None if usuario is None else usuario_a_dominio(usuario)

    def listar_asesores(self, marca_id: int) -> list[Usuario]:
        usuarios = self.sesion.scalars(
            select(UsuarioModelo)
            .join(UsuarioModelo.asesor)
            .where(AsesorModelo.marca_id == marca_id)
            .order_by(UsuarioModelo.id)
        ).all()
        return [usuario_a_dominio(usuario) for usuario in usuarios]
