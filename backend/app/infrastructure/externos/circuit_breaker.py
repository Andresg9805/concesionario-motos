import time
from collections.abc import Awaitable, Callable
from enum import StrEnum
from typing import Generic, TypeVar

T = TypeVar("T")


class EstadoCircuito(StrEnum):
    CERRADO = "CERRADO"
    ABIERTO = "ABIERTO"
    SEMIABIERTO = "SEMIABIERTO"


class RespaldoNoDisponibleError(Exception):
    pass


class CircuitBreaker(Generic[T]):
    def __init__(
        self,
        maximo_fallos: int = 3,
        segundos_apertura: float = 60.0,
        reloj: Callable[[], float] = time.monotonic,
    ) -> None:
        self._maximo_fallos = maximo_fallos
        self._segundos_apertura = segundos_apertura
        self._reloj = reloj
        self._estado = EstadoCircuito.CERRADO
        self._fallos = 0
        self._abierto_en = 0.0
        self._prueba_en_curso = False
        self._ultimo_valor: T | None = None

    @property
    def estado(self) -> EstadoCircuito:
        if (
            self._estado == EstadoCircuito.ABIERTO
            and self._reloj() - self._abierto_en >= self._segundos_apertura
        ):
            return EstadoCircuito.SEMIABIERTO
        return self._estado

    @property
    def fallos_consecutivos(self) -> int:
        return self._fallos

    @property
    def ultimo_valor(self) -> T | None:
        return self._ultimo_valor

    async def ejecutar(self, llamada: Callable[[], Awaitable[T]]) -> T:
        estado = self.estado
        if estado == EstadoCircuito.ABIERTO:
            return self._respaldo()
        es_prueba = estado == EstadoCircuito.SEMIABIERTO
        if es_prueba:
            if self._prueba_en_curso:
                return self._respaldo()
            self._prueba_en_curso = True
        try:
            valor = await llamada()
        except Exception:
            self._registrar_fallo(es_prueba)
            return self._respaldo()
        finally:
            if es_prueba:
                self._prueba_en_curso = False
        self._fallos = 0
        self._estado = EstadoCircuito.CERRADO
        self._ultimo_valor = valor
        return valor

    def _registrar_fallo(self, es_prueba: bool) -> None:
        self._fallos += 1
        if es_prueba or self._fallos >= self._maximo_fallos:
            self._estado = EstadoCircuito.ABIERTO
            self._abierto_en = self._reloj()

    def _respaldo(self) -> T:
        if self._ultimo_valor is None:
            raise RespaldoNoDisponibleError("No hay un valor de respaldo guardado")
        return self._ultimo_valor
