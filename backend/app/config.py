import os
from dataclasses import dataclass
from functools import lru_cache

LONGITUD_MINIMA_SECRETO = 32


@dataclass(frozen=True)
class Configuracion:
    jwt_secreto: str
    jwt_expira_minutos: int


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
    )
