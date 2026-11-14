from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.atencion import Rol

PATRON_CORREO = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PATRON_CELULAR = r"^3\d{9}$"
MAXIMO_BYTES_CONTRASENA = 72


class EntradaEstricta(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RegistroEntrada(EntradaEstricta):
    nombre: str = Field(min_length=3, max_length=120, examples=["Ana Pérez"])
    correo: str = Field(max_length=254, pattern=PATRON_CORREO, examples=["ana@correo.com"])
    celular: str = Field(pattern=PATRON_CELULAR, examples=["3001234567"])
    contrasena: str = Field(min_length=8, max_length=72, examples=["clave1234"])

    @field_validator("correo")
    @classmethod
    def normalizar_correo(cls, correo: str) -> str:
        return correo.lower()

    @field_validator("contrasena")
    @classmethod
    def validar_bytes_contrasena(cls, contrasena: str) -> str:
        if len(contrasena.encode("utf-8")) > MAXIMO_BYTES_CONTRASENA:
            raise ValueError("La contraseña no puede superar 72 bytes")
        return contrasena


class LoginEntrada(EntradaEstricta):
    correo: str = Field(max_length=254, examples=["cliente@correo.com"])
    contrasena: str = Field(min_length=1, max_length=72, examples=["clave1234"])


class UsuarioSalida(BaseModel):
    id: int
    nombre: str
    correo: str
    celular: str
    rol: Rol
    marca: str | None = None


class TokenSalida(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SesionSalida(BaseModel):
    id: int
    nombre: str
    rol: Rol
    marca: str | None = None
