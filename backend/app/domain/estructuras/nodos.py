from typing import Generic, TypeVar

from app.domain.catalogo import Moto

T = TypeVar("T")


class Nodo(Generic[T]):
    def __init__(self, valor: T) -> None:
        self.valor = valor
        self.siguiente: Nodo[T] | None = None


class NodoArbol:
    def __init__(self, moto: Moto) -> None:
        self.moto = moto
        self.izquierdo: NodoArbol | None = None
        self.derecho: NodoArbol | None = None
