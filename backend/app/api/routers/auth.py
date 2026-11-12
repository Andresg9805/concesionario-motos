from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencias import (
    obtener_iniciar_sesion,
    obtener_registrar_cliente,
    obtener_sesion_actual,
)
from app.api.schemas.auth import (
    LoginEntrada,
    RegistroEntrada,
    SesionSalida,
    TokenSalida,
    UsuarioSalida,
)
from app.application.autenticacion import DatosRegistro, IniciarSesion, RegistrarCliente
from app.domain.excepciones import CorreoYaRegistradoError, CredencialesInvalidasError
from app.domain.seguridad import DatosToken

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/registro",
    status_code=status.HTTP_201_CREATED,
    response_model=UsuarioSalida,
    responses={status.HTTP_409_CONFLICT: {"description": "El correo ya está registrado"}},
)
def registrar(
    entrada: RegistroEntrada,
    caso_de_uso: Annotated[RegistrarCliente, Depends(obtener_registrar_cliente)],
) -> UsuarioSalida:
    try:
        usuario = caso_de_uso.ejecutar(DatosRegistro(**entrada.model_dump()))
    except CorreoYaRegistradoError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error.mensaje) from error
    return UsuarioSalida(
        id=usuario.id,
        nombre=usuario.nombre,
        correo=usuario.correo,
        celular=usuario.telefono,
        rol=usuario.rol,
        marca=usuario.marca_especialidad.nombre.lower() if usuario.marca_especialidad else None,
    )


@router.post(
    "/login",
    response_model=TokenSalida,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Credenciales incorrectas"}},
)
def iniciar_sesion(
    entrada: LoginEntrada,
    caso_de_uso: Annotated[IniciarSesion, Depends(obtener_iniciar_sesion)],
) -> TokenSalida:
    try:
        token = caso_de_uso.ejecutar(entrada.correo, entrada.contrasena)
    except CredencialesInvalidasError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error.mensaje,
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    return TokenSalida(access_token=token)


@router.get("/yo", response_model=SesionSalida)
def sesion_actual(sesion: Annotated[DatosToken, Depends(obtener_sesion_actual)]) -> SesionSalida:
    return SesionSalida(
        id=sesion.usuario_id, nombre=sesion.nombre, rol=sesion.rol, marca=sesion.marca
    )
