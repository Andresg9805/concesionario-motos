from dataclasses import replace
from itertools import count
from threading import Lock

from app.domain.atencion import Cliente, Rol, Usuario
from app.domain.puertos import RepositorioClientes, RepositorioUsuarios


class RepositorioUsuariosEnMemoria(RepositorioUsuarios):
    def __init__(self) -> None:
        self._usuarios: dict[int, Usuario] = {}
        self._ids = count(1)
        self._candado = Lock()

    def guardar(self, usuario: Usuario) -> Usuario:
        with self._candado:
            existente = self._buscar(usuario.correo)
            if existente is not None and existente.id != usuario.id:
                raise ValueError("Ya existe un usuario con ese correo")
            guardado = usuario if usuario.id is not None else replace(usuario, id=next(self._ids))
            self._usuarios[guardado.id] = guardado
            return guardado

    def buscar_por_correo(self, correo: str) -> Usuario | None:
        with self._candado:
            return self._buscar(correo)

    def listar_asesores(self, marca_id: int) -> list[Usuario]:
        with self._candado:
            return [
                usuario
                for usuario in self._usuarios.values()
                if usuario.rol == Rol.ASESOR
                and usuario.marca_especialidad is not None
                and usuario.marca_especialidad.id == marca_id
            ]

    def _buscar(self, correo: str) -> Usuario | None:
        normalizado = correo.strip().lower()
        return next((u for u in self._usuarios.values() if u.correo == normalizado), None)


class RepositorioClientesEnMemoria(RepositorioClientes):
    def __init__(self) -> None:
        self._clientes: dict[int, Cliente] = {}
        self._ids = count(1)
        self._candado = Lock()

    def guardar(self, cliente: Cliente) -> Cliente:
        with self._candado:
            guardado = cliente if cliente.id is not None else replace(cliente, id=next(self._ids))
            self._clientes[guardado.id] = guardado
            return guardado

    def buscar_por_correo(self, correo: str) -> Cliente | None:
        normalizado = correo.strip().lower()
        with self._candado:
            return next((c for c in self._clientes.values() if c.correo == normalizado), None)
