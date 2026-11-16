import asyncio
import logging
from collections.abc import Awaitable, Callable

from app.application.pedidos import ExpirarReservas

INTERVALO_EXPIRAR_RESERVAS_SEGUNDOS = 60

registro = logging.getLogger(__name__)


async def ciclo_expirar_reservas(
    obtener_caso_de_uso: Callable[[], ExpirarReservas],
    intervalo: float = INTERVALO_EXPIRAR_RESERVAS_SEGUNDOS,
    dormir: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> None:
    while True:
        await dormir(intervalo)
        try:
            obtener_caso_de_uso().ejecutar()
        except Exception:
            registro.exception("Falló la expiración periódica de reservas")
