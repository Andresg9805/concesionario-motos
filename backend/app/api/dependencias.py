import os
import secrets
from collections.abc import Callable
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.atencion import (
    AsignacionAtencion,
    AtenderSiguienteTestDrive,
    CambiarEstadoCotizacion,
    ConsultarSeguimiento,
    ListarAtencionesAsesor,
    ListarColaTestDrives,
    Reloj,
    SolicitarCotizacion,
    SolicitarTestDrive,
    reloj_colombia,
)
from app.application.autenticacion import IniciarSesion, RegistrarCliente
from app.application.motos import (
    BuscarMotosPorCuota,
    CalcularCostoReal,
    ListarMarcas,
    ListarMotos,
    ObtenerMoto,
)
from app.config import obtener_configuracion
from app.domain.atencion import Rol
from app.domain.excepciones import TokenInvalidoError
from app.domain.puertos import (
    RepositorioBusquedas,
    RepositorioClientes,
    RepositorioCotizaciones,
    RepositorioMarcas,
    RepositorioMotos,
    RepositorioParametros,
    RepositorioSimulaciones,
    RepositorioTestDrives,
    RepositorioUsuarios,
)
from app.domain.seguridad import DatosToken, EmisorTokens, HasheadorContrasenas
from app.infrastructure.memoria.atencion import (
    RepositorioCotizacionesEnMemoria,
    RepositorioTestDrivesEnMemoria,
)
from app.infrastructure.memoria.catalogo import (
    RepositorioBusquedasEnMemoria,
    RepositorioMarcasEnMemoria,
    RepositorioMotosEnMemoria,
    RepositorioParametrosEnMemoria,
    RepositorioSimulacionesEnMemoria,
)
from app.infrastructure.memoria.datos_prueba import asesores_iniciales
from app.infrastructure.memoria.usuarios import (
    RepositorioClientesEnMemoria,
    RepositorioUsuariosEnMemoria,
)
from app.infrastructure.seguridad.bcrypt_hasheador import HasheadorBcrypt
from app.infrastructure.seguridad.jwt_emisor import EmisorTokensJWT

esquema_bearer = HTTPBearer(auto_error=False)


@lru_cache
def obtener_repositorio_usuarios() -> RepositorioUsuarios:
    usuarios = RepositorioUsuariosEnMemoria()
    contrasena = os.environ.get("CONTRASENA_ASESORES_DEMO") or secrets.token_urlsafe(32)
    hash_contrasena = obtener_hasheador().hashear(contrasena)
    for asesor in asesores_iniciales(hash_contrasena):
        usuarios.guardar(asesor)
    return usuarios


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


@lru_cache
def obtener_repositorio_marcas() -> RepositorioMarcas:
    return RepositorioMarcasEnMemoria()


@lru_cache
def obtener_repositorio_motos() -> RepositorioMotos:
    return RepositorioMotosEnMemoria()


@lru_cache
def obtener_repositorio_parametros() -> RepositorioParametros:
    return RepositorioParametrosEnMemoria()


@lru_cache
def obtener_repositorio_busquedas() -> RepositorioBusquedas:
    return RepositorioBusquedasEnMemoria()


@lru_cache
def obtener_repositorio_simulaciones() -> RepositorioSimulaciones:
    return RepositorioSimulacionesEnMemoria()


def obtener_listar_marcas(
    marcas: Annotated[RepositorioMarcas, Depends(obtener_repositorio_marcas)],
) -> ListarMarcas:
    return ListarMarcas(marcas)


def obtener_listar_motos(
    motos: Annotated[RepositorioMotos, Depends(obtener_repositorio_motos)],
) -> ListarMotos:
    return ListarMotos(motos)


def obtener_obtener_moto(
    motos: Annotated[RepositorioMotos, Depends(obtener_repositorio_motos)],
) -> ObtenerMoto:
    return ObtenerMoto(motos)


def obtener_buscar_por_cuota(
    motos: Annotated[RepositorioMotos, Depends(obtener_repositorio_motos)],
    parametros: Annotated[RepositorioParametros, Depends(obtener_repositorio_parametros)],
    busquedas: Annotated[RepositorioBusquedas, Depends(obtener_repositorio_busquedas)],
    simulaciones: Annotated[RepositorioSimulaciones, Depends(obtener_repositorio_simulaciones)],
) -> BuscarMotosPorCuota:
    return BuscarMotosPorCuota(motos, parametros, busquedas, simulaciones)


def obtener_calcular_costo_real(
    motos: Annotated[RepositorioMotos, Depends(obtener_repositorio_motos)],
    parametros: Annotated[RepositorioParametros, Depends(obtener_repositorio_parametros)],
) -> CalcularCostoReal:
    return CalcularCostoReal(motos, parametros)


@lru_cache
def obtener_repositorio_cotizaciones() -> RepositorioCotizaciones:
    return RepositorioCotizacionesEnMemoria()


@lru_cache
def obtener_repositorio_test_drives() -> RepositorioTestDrives:
    return RepositorioTestDrivesEnMemoria()


def obtener_reloj_atencion() -> Reloj:
    return reloj_colombia


def obtener_asignacion_atencion(
    motos: Annotated[RepositorioMotos, Depends(obtener_repositorio_motos)],
    clientes: Annotated[RepositorioClientes, Depends(obtener_repositorio_clientes)],
    usuarios: Annotated[RepositorioUsuarios, Depends(obtener_repositorio_usuarios)],
    cotizaciones: Annotated[RepositorioCotizaciones, Depends(obtener_repositorio_cotizaciones)],
    test_drives: Annotated[RepositorioTestDrives, Depends(obtener_repositorio_test_drives)],
) -> AsignacionAtencion:
    return AsignacionAtencion(motos, clientes, usuarios, cotizaciones, test_drives)


def obtener_solicitar_cotizacion(
    asignacion: Annotated[AsignacionAtencion, Depends(obtener_asignacion_atencion)],
    cotizaciones: Annotated[RepositorioCotizaciones, Depends(obtener_repositorio_cotizaciones)],
    parametros: Annotated[RepositorioParametros, Depends(obtener_repositorio_parametros)],
    reloj: Annotated[Reloj, Depends(obtener_reloj_atencion)],
) -> SolicitarCotizacion:
    return SolicitarCotizacion(asignacion, cotizaciones, parametros, reloj)


def obtener_solicitar_test_drive(
    asignacion: Annotated[AsignacionAtencion, Depends(obtener_asignacion_atencion)],
    test_drives: Annotated[RepositorioTestDrives, Depends(obtener_repositorio_test_drives)],
    reloj: Annotated[Reloj, Depends(obtener_reloj_atencion)],
) -> SolicitarTestDrive:
    return SolicitarTestDrive(asignacion, test_drives, reloj)


def obtener_consultar_seguimiento(
    cotizaciones: Annotated[RepositorioCotizaciones, Depends(obtener_repositorio_cotizaciones)],
    test_drives: Annotated[RepositorioTestDrives, Depends(obtener_repositorio_test_drives)],
) -> ConsultarSeguimiento:
    return ConsultarSeguimiento(cotizaciones, test_drives)


def obtener_listar_atenciones_asesor(
    cotizaciones: Annotated[RepositorioCotizaciones, Depends(obtener_repositorio_cotizaciones)],
) -> ListarAtencionesAsesor:
    return ListarAtencionesAsesor(cotizaciones)


def obtener_cambiar_estado_cotizacion(
    cotizaciones: Annotated[RepositorioCotizaciones, Depends(obtener_repositorio_cotizaciones)],
) -> CambiarEstadoCotizacion:
    return CambiarEstadoCotizacion(cotizaciones)


def obtener_listar_cola_test_drives(
    test_drives: Annotated[RepositorioTestDrives, Depends(obtener_repositorio_test_drives)],
) -> ListarColaTestDrives:
    return ListarColaTestDrives(test_drives)


def obtener_atender_siguiente_test_drive(
    test_drives: Annotated[RepositorioTestDrives, Depends(obtener_repositorio_test_drives)],
) -> AtenderSiguienteTestDrive:
    return AtenderSiguienteTestDrive(test_drives)
