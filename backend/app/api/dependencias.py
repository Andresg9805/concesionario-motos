from collections.abc import Callable
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.autenticacion import IniciarSesion, RegistrarCliente
from app.config import obtener_configuracion
from app.domain.atencion import Rol
from app.domain.excepciones import TokenInvalidoError
from app.domain.puertos import RepositorioClientes, RepositorioUsuarios
from app.domain.seguridad import DatosToken, EmisorTokens, HasheadorContrasenas
from app.infrastructure.memoria.usuarios import (
    RepositorioClientesEnMemoria,
    RepositorioUsuariosEnMemoria,
)
from app.infrastructure.seguridad.bcrypt_hasheador import HasheadorBcrypt
from app.infrastructure.seguridad.jwt_emisor import EmisorTokensJWT

esquema_bearer = HTTPBearer(auto_error=False)


@lru_cache
def obtener_repositorio_usuarios() -> RepositorioUsuarios:
    return RepositorioUsuariosEnMemoria()


@lru_cache
def obtener_repositorio_clientes() -> RepositorioClientes:
    return RepositorioClientesEnMemoria()


@lru_cache
def obtener_hasheador() -> HasheadorContrasenas:
    return HasheadorBcrypt()


@lru_cache
def obtener_hash_senuelo() -> str:
    return obtener_hasheador().hashear("contrasena-senuelo-candela")


@lru_cache
def obtener_emisor_tokens() -> EmisorTokens:
    configuracion = obtener_configuracion()
    return EmisorTokensJWT(configuracion.jwt_secreto, configuracion.jwt_expira_minutos)


def obtener_registrar_cliente(
    usuarios: Annotated[RepositorioUsuarios, Depends(obtener_repositorio_usuarios)],
    clientes: Annotated[RepositorioClientes, Depends(obtener_repositorio_clientes)],
    hasheador: Annotated[HasheadorContrasenas, Depends(obtener_hasheador)],
) -> RegistrarCliente:
    return RegistrarCliente(usuarios, clientes, hasheador)


def obtener_iniciar_sesion(
    usuarios: Annotated[RepositorioUsuarios, Depends(obtener_repositorio_usuarios)],
    hasheador: Annotated[HasheadorContrasenas, Depends(obtener_hasheador)],
    emisor: Annotated[EmisorTokens, Depends(obtener_emisor_tokens)],
    hash_senuelo: Annotated[str, Depends(obtener_hash_senuelo)],
) -> IniciarSesion:
    return IniciarSesion(usuarios, hasheador, emisor, hash_senuelo)


def obtener_sesion_actual(
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
    emisor: Annotated[EmisorTokens, Depends(obtener_emisor_tokens)],
) -> DatosToken:
    no_autenticado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credenciales is None or credenciales.scheme.lower() != "bearer":
        raise no_autenticado
    try:
        return emisor.leer(credenciales.credentials)
    except TokenInvalidoError as error:
        raise no_autenticado from error


def requerir_rol(*roles: Rol | str) -> Callable[[DatosToken], DatosToken]:
    permitidos = {Rol(rol) for rol in roles}

    def verificar(
        sesion: Annotated[DatosToken, Depends(obtener_sesion_actual)],
    ) -> DatosToken:
        if sesion.rol not in permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para esta acción",
            )
        return sesion

    return verificar
