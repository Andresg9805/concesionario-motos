from app.domain.catalogo import Moto
from app.domain.estructuras.nodos import NodoArbol


class ArbolMotosPorPrecio:
    def __init__(self) -> None:
        self._raiz: NodoArbol | None = None
        self._cantidad = 0

    def insertar(self, moto: Moto) -> None:
        nuevo = NodoArbol(moto)
        self._cantidad += 1
        if self._raiz is None:
            self._raiz = nuevo
            return
        actual = self._raiz
        while True:
            if moto.precio_cop < actual.moto.precio_cop:
                if actual.izquierdo is None:
                    actual.izquierdo = nuevo
                    return
                actual = actual.izquierdo
            else:
                if actual.derecho is None:
                    actual.derecho = nuevo
                    return
                actual = actual.derecho

    def buscar_rango(self, minimo: int, maximo: int) -> list[Moto]:
        encontradas: list[Moto] = []
        if minimo <= maximo:
            self._buscar_rango(self._raiz, minimo, maximo, encontradas)
        return encontradas

    def _buscar_rango(
        self, nodo: NodoArbol | None, minimo: int, maximo: int, encontradas: list[Moto]
    ) -> None:
        if nodo is None:
            return
        precio = nodo.moto.precio_cop
        if precio > minimo:
            self._buscar_rango(nodo.izquierdo, minimo, maximo, encontradas)
        if minimo <= precio <= maximo:
            encontradas.append(nodo.moto)
        if precio <= maximo:
            self._buscar_rango(nodo.derecho, minimo, maximo, encontradas)

    def inorden(self) -> list[Moto]:
        motos: list[Moto] = []
        self._inorden(self._raiz, motos)
        return motos

    def _inorden(self, nodo: NodoArbol | None, motos: list[Moto]) -> None:
        if nodo is None:
            return
        self._inorden(nodo.izquierdo, motos)
        motos.append(nodo.moto)
        self._inorden(nodo.derecho, motos)

    def tamano(self) -> int:
        return self._cantidad

    def esta_vacio(self) -> bool:
        return self._raiz is None
