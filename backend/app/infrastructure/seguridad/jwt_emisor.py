from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import jwt

from app.domain.atencion import Rol, Usuario
from app.domain.excepciones import TokenInvalidoError
from app.domain.seguridad import DatosToken, EmisorTokens

ALGORITMO = "HS256"
CAMPOS_OBLIGATORIOS = ["sub", "nombre", "rol", "exp"]


class EmisorTokensJWT(EmisorTokens):
    def __init__(
        self,
        secreto: str,
        minutos_expiracion: int,
        reloj: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._secreto = secreto
        self._minutos_expiracion = minutos_expiracion
        self._reloj = reloj

    def emitir(self, usuario: Usuario) -> str:
        if usuario.id is None:
            raise ValueError("El usuario debe estar guardado para emitir un token")
        marca = usuario.marca_especialidad
        payload = {
            "sub": str(usuario.id),
            "nombre": usuario.nombre,
            "rol": usuario.rol.value,
            "marca": marca.nombre.lower() if marca else None,
            "exp": self._reloj() + timedelta(minutes=self._minutos_expiracion),
        }
        return jwt.encode(payload, self._secreto, algorithm=ALGORITMO)

    def leer(self, token: str) -> DatosToken:
        try:
            payload = jwt.decode(
                token,
                self._secreto,
                algorithms=[ALGORITMO],
                options={"require": CAMPOS_OBLIGATORIOS},
            )
            return DatosToken(
                usuario_id=int(payload["sub"]),
                nombre=payload["nombre"],
                rol=Rol(payload["rol"]),
                marca=payload.get("marca"),
            )
        except (jwt.PyJWTError, ValueError, KeyError) as error:
            raise TokenInvalidoError("Token inválido o vencido") from error
