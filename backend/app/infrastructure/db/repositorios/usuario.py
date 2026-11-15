
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.atencion import Rol
from app.domain.atencion import Usuario as UsuarioDominio
from app.domain.catalogo import Marca as MarcaDominio
from app.domain.puertos import RepositorioUsuarios
from app.infrastructure.models.usuario import Usuario as UsuarioModelo


class RepositorioUsuariosSQLAlchemy(RepositorioUsuarios):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    @staticmethod
    def _a_dominio(usuario: UsuarioModelo) -> UsuarioDominio:
        marca = None

        if usuario.marca_especialidad is not None:
            marca = MarcaDominio(
                id=usuario.marca_especialidad.id,
                nombre=usuario.marca_especialidad.nombre,
                color_hex=usuario.marca_especialidad.color_hex,
                descripcion=usuario.marca_especialidad.descripcion or "",
            )

        return UsuarioDominio(
            id=usuario.id,
            nombre=usuario.nombre,
            correo=usuario.correo,
            telefono=usuario.telefono,
            hash_contrasena=usuario.hash_contrasena,
            rol=Rol(usuario.rol),
            marca_especialidad=marca,
        )

    def guardar(self, usuario: UsuarioDominio) -> UsuarioDominio:
        modelo = self.sesion.get(UsuarioModelo, usuario.id) if usuario.id else None

        if modelo is None:
            modelo = UsuarioModelo()

        modelo.nombre = usuario.nombre
        modelo.correo = usuario.correo.strip().lower()
        modelo.telefono = usuario.telefono
        modelo.hash_contrasena = usuario.hash_contrasena
        modelo.rol = usuario.rol.value
        modelo.marca_especialidad_id = (
            usuario.marca_especialidad.id
            if usuario.marca_especialidad is not None
            else None
        )

        self.sesion.add(modelo)

        try:
            self.sesion.flush()
        except IntegrityError as error:
            self.sesion.rollback()
            raise ValueError(
                "Ya existe un usuario con ese correo"
            ) from error

        return self._a_dominio(modelo)

    def buscar_por_correo(self, correo: str) -> UsuarioDominio | None:
        consulta = select(UsuarioModelo).where(
            UsuarioModelo.correo == correo.strip().lower()
        )
        usuario = self.sesion.scalars(consulta).first()

        if usuario is None:
            return None

        return self._a_dominio(usuario)

    def buscar_por_id(self, id: int) -> UsuarioDominio | None:
        usuario = self.sesion.get(UsuarioModelo, id)

        if usuario is None:
            return None

        return self._a_dominio(usuario)

    def listar_asesores(self, marca_id: int) -> list[UsuarioDominio]:
        consulta = (
            select(UsuarioModelo)
            .where(
                UsuarioModelo.rol == Rol.ASESOR.value,
                UsuarioModelo.marca_especialidad_id == marca_id,
            )
            .order_by(UsuarioModelo.id)
        )

        usuarios = self.sesion.scalars(consulta).all()
        return [self._a_dominio(usuario) for usuario in usuarios]
