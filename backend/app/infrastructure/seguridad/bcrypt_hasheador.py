import bcrypt

from app.domain.seguridad import HasheadorContrasenas

RONDAS_BCRYPT = 12


class HasheadorBcrypt(HasheadorContrasenas):
    def __init__(self, rondas: int = RONDAS_BCRYPT) -> None:
        self._rondas = rondas

    def hashear(self, contrasena: str) -> str:
        sal = bcrypt.gensalt(rounds=self._rondas)
        return bcrypt.hashpw(contrasena.encode("utf-8"), sal).decode("utf-8")

    def verificar(self, contrasena: str, hash_contrasena: str) -> bool:
        try:
            return bcrypt.checkpw(contrasena.encode("utf-8"), hash_contrasena.encode("utf-8"))
        except ValueError:
            return False
