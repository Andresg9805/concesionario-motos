import os
from datetime import date
from typing import Any

import httpx

from app.domain.catalogo import TasaCambio
from app.domain.excepciones import TasaNoDisponibleError
from app.domain.puertos import ProveedorTasaCambio
from app.infrastructure.externos.circuit_breaker import (
    CircuitBreaker,
    RespaldoNoDisponibleError,
)

URL_TRM = "https://www.datos.gov.co/resource/32sa-8pi3.json?$order=vigenciadesde%20DESC&$limit=1"
SEGUNDOS_ESPERA_TRM = 3.0


def url_trm_configurada() -> str:
    return os.environ.get("TRM_API_URL", "").strip() or URL_TRM


class ProveedorTasaCambioDatosGov(ProveedorTasaCambio):
    def __init__(
        self,
        url: str = URL_TRM,
        circuito: CircuitBreaker[TasaCambio] | None = None,
        transporte: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._url = url
        self._circuito = circuito or CircuitBreaker[TasaCambio]()
        self._transporte = transporte

    @property
    def circuito(self) -> CircuitBreaker[TasaCambio]:
        return self._circuito

    async def obtener_trm(self) -> TasaCambio:
        try:
            return await self._circuito.ejecutar(self._consultar)
        except RespaldoNoDisponibleError as error:
            raise TasaNoDisponibleError("La TRM no está disponible por ahora") from error

    async def _consultar(self) -> TasaCambio:
        async with httpx.AsyncClient(
            timeout=SEGUNDOS_ESPERA_TRM, transport=self._transporte
        ) as cliente:
            respuesta = await cliente.get(self._url)
            respuesta.raise_for_status()
            filas: list[dict[str, Any]] = respuesta.json()
        if not filas:
            raise ValueError("datos.gov.co no devolvió ninguna TRM")
        fila = filas[0]
        return TasaCambio(valor=float(fila["valor"]), fecha=_fecha(fila))


def _fecha(fila: dict[str, Any]) -> date:
    return date.fromisoformat(str(fila["vigenciadesde"])[:10])
