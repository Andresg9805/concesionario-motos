import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Protocol

INTERVALO_EXPIRAR_RESERVAS_SEGUNDOS = 60

registro = logging.getLogger(__name__)


class CasoDeUsoPeriodico(Protocol):
    def ejecutar(self) -> None: ...


async def ciclo_expirar_reservas(
    obtener_caso_de_uso: Callable[[], CasoDeUsoPeriodico],
    intervalo: float = INTERVALO_EXPIRAR_RESERVAS_SEGUNDOS,
    dormir: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> None:
    while True:
        await dormir(intervalo)
        try:
            obtener_caso_de_uso().ejecutar()
        except Exception:
            registro.exception("Falló la expiración periódica de reservas")
