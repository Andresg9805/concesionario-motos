from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.atencion import Rol, Usuario


@dataclass(frozen=True)
class DatosToken:
    usuario_id: int
    nombre: str
    rol: Rol
    marca: str | None


class HasheadorContrasenas(ABC):
    @abstractmethod
    def hashear(self, contrasena: str) -> str: ...

    @abstractmethod
    def verificar(self, contrasena: str, hash_contrasena: str) -> bool: ...


class EmisorTokens(ABC):
    @abstractmethod
    def emitir(self, usuario: Usuario) -> str: ...

    @abstractmethod
    def leer(self, token: str) -> DatosToken: ...
