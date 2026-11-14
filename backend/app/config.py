import os
from dataclasses import dataclass
from functools import lru_cache

from app.domain.tienda import MINUTOS_RESERVA

LONGITUD_MINIMA_SECRETO = 32
URL_WOMPI_SANDBOX = "https://sandbox.wompi.co/v1"


@dataclass(frozen=True)
class Configuracion:
    jwt_secreto: str
    jwt_expira_minutos: int
    minutos_reserva_pedido: int = MINUTOS_RESERVA


@dataclass(frozen=True)
class ConfiguracionWompi:
    api_url: str
    llave_publica: str
    secreto_integridad: str
    secreto_eventos: str


@lru_cache
def obtener_configuracion() -> Configuracion:
    secreto = os.environ.get("JWT_SECRET", "")
    if len(secreto) < LONGITUD_MINIMA_SECRETO:
        raise RuntimeError(
            f"JWT_SECRET debe estar definido y tener al menos {LONGITUD_MINIMA_SECRETO} caracteres"
        )
    return Configuracion(
        jwt_secreto=secreto,
        jwt_expira_minutos=int(os.environ.get("JWT_EXPIRA_MINUTOS", "60")),
        minutos_reserva_pedido=int(os.environ.get("MINUTOS_RESERVA_PEDIDO", str(MINUTOS_RESERVA))),
    )


@lru_cache
def obtener_configuracion_wompi() -> ConfiguracionWompi:
    variables = {
        nombre: os.environ.get(nombre, "").strip()
        for nombre in ("WOMPI_LLAVE_PUBLICA", "WOMPI_SECRETO_INTEGRIDAD", "WOMPI_SECRETO_EVENTOS")
    }
    faltantes = [nombre for nombre, valor in variables.items() if not valor]
    if faltantes:
        raise RuntimeError(f"Faltan variables de entorno de Wompi: {', '.join(faltantes)}")
    return ConfiguracionWompi(
        api_url=os.environ.get("WOMPI_API_URL", URL_WOMPI_SANDBOX).rstrip("/"),
        llave_publica=variables["WOMPI_LLAVE_PUBLICA"],
        secreto_integridad=variables["WOMPI_SECRETO_INTEGRIDAD"],
        secreto_eventos=variables["WOMPI_SECRETO_EVENTOS"],
    )
