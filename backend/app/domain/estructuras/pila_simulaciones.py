from app.domain.catalogo import PlanCredito
from app.domain.estructuras.nodos import Nodo


class PilaSimulaciones:
    def __init__(self) -> None:
        self._cima: Nodo[PlanCredito] | None = None
        self._cantidad = 0

    def apilar(self, plan: PlanCredito) -> None:
        nodo = Nodo(plan)
        nodo.siguiente = self._cima
        self._cima = nodo
        self._cantidad += 1

    def desapilar(self) -> PlanCredito:
        if self._cima is None:
            raise IndexError("No hay simulaciones para deshacer")
        plan = self._cima.valor
        self._cima = self._cima.siguiente
        self._cantidad -= 1
        return plan

    def ver_cima(self) -> PlanCredito:
        if self._cima is None:
            raise IndexError("No hay simulaciones guardadas")
        return self._cima.valor

    def esta_vacia(self) -> bool:
        return self._cima is None

    def tamano(self) -> int:
        return self._cantidad
