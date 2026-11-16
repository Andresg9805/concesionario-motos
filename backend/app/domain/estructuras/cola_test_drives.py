from collections.abc import Iterator

from app.domain.atencion import TestDrive
from app.domain.estructuras.nodos import Nodo


class ColaTestDrives:
    def __init__(self) -> None:
        self._frente: Nodo[TestDrive] | None = None
        self._final: Nodo[TestDrive] | None = None
        self._cantidad = 0

    def encolar(self, test_drive: TestDrive) -> None:
        nodo = Nodo(test_drive)

        if self._final is None:
            self._frente = nodo
        else:
            self._final.siguiente = nodo

        self._final = nodo
        self._cantidad += 1

    def desencolar(self) -> TestDrive:
        if self._frente is None:
            raise IndexError("No hay test drives pendientes")

        test_drive = self._frente.valor
        self._frente = self._frente.siguiente
        self._cantidad -= 1

        if self._frente is None:
            self._final = None

        return test_drive

    def frente(self) -> TestDrive:
        if self._frente is None:
            raise IndexError("No hay test drives pendientes")

        return self._frente.valor

    def esta_vacia(self) -> bool:
        return self._frente is None

    def __len__(self) -> int:
        return self._cantidad

    def __iter__(self) -> Iterator[TestDrive]:
        actual = self._frente

        while actual is not None:
            yield actual.valor
            actual = actual.siguiente


class AgendaTestDrives:
    def __init__(self) -> None:
        self._colas: dict[int, ColaTestDrives] = {}

    def encolar(self, asesor_id: int, test_drive: TestDrive) -> None:
        if asesor_id not in self._colas:
            self._colas[asesor_id] = ColaTestDrives()

        self._colas[asesor_id].encolar(test_drive)

    def siguiente(self, asesor_id: int) -> TestDrive:
        cola = self._colas.get(asesor_id)

        if cola is None:
            raise IndexError("El asesor no tiene test drives pendientes")

        return cola.desencolar()

    def pendientes(self, asesor_id: int) -> int:
        cola = self._colas.get(asesor_id)
        return len(cola) if cola is not None else 0
