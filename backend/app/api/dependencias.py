import os
import secrets
from collections.abc import Callable, Iterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.admin import (
    ActualizarAccesorio,
    ActualizarMoto,
    ActualizarParametros,
    AvanzarEnvio,
    CrearAccesorio,
    CrearMoto,
    EliminarAccesorio,
    EliminarMoto,
    ListarPedidosAdmin,
    ObtenerParametros,
)
from app.application.atencion import (
    AsignacionAtencion,
    AtenderSiguienteTestDrive,
    CambiarEstadoCotizacion,
    ConsultarSeguimiento,
    ListarAtencionesAsesor,
    ListarColaTestDrives,
    ListarMisCotizaciones,
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
    ObtenerDetalleMoto,
)
from app.application.pedidos import (
    ConfirmarPago,
    CrearPedido,
    ExpirarReservas,
    ListarPedidosPropios,
    ObtenerPedidoPropio,
    ProcesarEventoPago,
    VerificarPago,
)
from app.application.tienda import (
    CrearDireccion,
    ListarAccesorios,
    ListarDepartamentos,
    ListarDireccionesPropias,
    ListarMunicipios,
    ObtenerAccesorio,
    ObtenerDepartamento,
    ObtenerDireccionPropia,
)
from app.config import (
    ALMACENAMIENTO_SQLITE,
    obtener_almacenamiento,
    obtener_configuracion,
    obtener_configuracion_wompi,
)
from app.domain.atencion import Rol
from app.domain.excepciones import TokenInvalidoError
from app.domain.puertos import (
    PasarelaPago,
    ProveedorTasaCambio,
    RepositorioAccesorios,
    RepositorioBusquedas,
    RepositorioClientes,
    RepositorioCotizaciones,
    RepositorioDirecciones,
    RepositorioEnvios,
    RepositorioMarcas,
    RepositorioMotos,
    RepositorioPagos,
    RepositorioParametros,
    RepositorioPedidos,
    RepositorioSimulaciones,
    RepositorioTestDrives,
    RepositorioUbicaciones,
    RepositorioUsuarios,
)
from app.domain.seguridad import DatosToken, EmisorTokens, HasheadorContrasenas
from app.infrastructure.db.conexion import SessionLocal
from app.infrastructure.db.repositorios.busqueda import RepositorioBusquedasSQLAlchemy
from app.infrastructure.db.repositorios.cotizacion import RepositorioCotizacionesSQLAlchemy
from app.infrastructure.db.repositorios.marca import RepositorioMarcasSQLAlchemy
from app.infrastructure.db.repositorios.moto import RepositorioMotosSQLAlchemy
from app.infrastructure.db.repositorios.parametros import RepositorioParametrosSQLAlchemy
from app.infrastructure.db.repositorios.pedidos import (
    RepositorioEnviosSQLAlchemy,
    RepositorioPagosSQLAlchemy,
    RepositorioPedidosSQLAlchemy,
)
from app.infrastructure.db.repositorios.test_drive import RepositorioTestDrivesSQLAlchemy
from app.infrastructure.db.repositorios.tienda import (
    RepositorioAccesoriosSQLAlchemy,
    RepositorioDireccionesSQLAlchemy,
    RepositorioUbicacionesSQLAlchemy,
)
from app.infrastructure.db.repositorios.usuario import (
    RepositorioClientesSQLAlchemy,
    RepositorioUsuariosSQLAlchemy,
)
from app.infrastructure.externos.trm import ProveedorTasaCambioDatosGov, url_trm_configurada
from app.infrastructure.externos.wompi import PasarelaWompi
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
from app.infrastructure.memoria.datos_prueba import administrador_inicial, asesores_iniciales
from app.infrastructure.memoria.pedidos import (
    RepositorioEnviosEnMemoria,
    RepositorioPagosEnMemoria,
    RepositorioPedidosEnMemoria,
)
from app.infrastructure.memoria.tienda import (
    RepositorioAccesoriosEnMemoria,
    RepositorioDireccionesEnMemoria,
    RepositorioUbicacionesEnMemoria,
)
from app.infrastructure.memoria.usuarios import (
    RepositorioClientesEnMemoria,
    RepositorioUsuariosEnMemoria,
)
from app.infrastructure.seguridad.bcrypt_hasheador import HasheadorBcrypt
from app.infrastructure.seguridad.jwt_emisor import EmisorTokensJWT

ALMACENAMIENTO = obtener_almacenamiento()
USA_SQLITE = ALMACENAMIENTO == ALMACENAMIENTO_SQLITE

esquema_bearer = HTTPBearer(auto_error=False)


def obtener_sesion() -> Iterator[Session]:
    sesion = SessionLocal()
    try:
        yield sesion
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    finally:
        sesion.close()


@lru_cache
def obtener_repositorio_usuarios_en_memoria() -> RepositorioUsuarios:
    usuarios = RepositorioUsuariosEnMemoria()
    contrasena = os.environ.get("CONTRASENA_ASESORES_DEMO") or secrets.token_urlsafe(32)
    hash_contrasena = obtener_hasheador().hashear(contrasena)
    for asesor in asesores_iniciales(hash_contrasena):
        usuarios.guardar(asesor)
    contrasena_admin = os.environ.get("CONTRASENA_ADMIN_DEMO") or secrets.token_urlsafe(32)
    usuarios.guardar(administrador_inicial(obtener_hasheador().hashear(contrasena_admin)))
    return usuarios


def obtener_repositorio_usuarios_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioUsuarios:
    return RepositorioUsuariosSQLAlchemy(sesion)


obtener_repositorio_usuarios: Callable[..., RepositorioUsuarios] = (
    obtener_repositorio_usuarios_sqlite if USA_SQLITE else obtener_repositorio_usuarios_en_memoria
)


@lru_cache
def obtener_repositorio_clientes_en_memoria() -> RepositorioClientes:
    return RepositorioClientesEnMemoria()


def obtener_repositorio_clientes_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioClientes:
    return RepositorioClientesSQLAlchemy(sesion)


obtener_repositorio_clientes: Callable[..., RepositorioClientes] = (
    obtener_repositorio_clientes_sqlite if USA_SQLITE else obtener_repositorio_clientes_en_memoria
)


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
def obtener_repositorio_marcas_en_memoria() -> RepositorioMarcas:
    return RepositorioMarcasEnMemoria()


def obtener_repositorio_marcas_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioMarcas:
    return RepositorioMarcasSQLAlchemy(sesion)


obtener_repositorio_marcas: Callable[..., RepositorioMarcas] = (
    obtener_repositorio_marcas_sqlite if USA_SQLITE else obtener_repositorio_marcas_en_memoria
)


@lru_cache
def obtener_repositorio_motos_en_memoria() -> RepositorioMotos:
    return RepositorioMotosEnMemoria()


def obtener_repositorio_motos_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioMotos:
    return RepositorioMotosSQLAlchemy(sesion)


obtener_repositorio_motos: Callable[..., RepositorioMotos] = (
    obtener_repositorio_motos_sqlite if USA_SQLITE else obtener_repositorio_motos_en_memoria
)


@lru_cache
def obtener_repositorio_parametros_en_memoria() -> RepositorioParametros:
    return RepositorioParametrosEnMemoria()


def obtener_repositorio_parametros_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioParametros:
    return RepositorioParametrosSQLAlchemy(sesion)


obtener_repositorio_parametros: Callable[..., RepositorioParametros] = (
    obtener_repositorio_parametros_sqlite
    if USA_SQLITE
    else obtener_repositorio_parametros_en_memoria
)


@lru_cache
def obtener_repositorio_busquedas_en_memoria() -> RepositorioBusquedas:
    return RepositorioBusquedasEnMemoria()


def obtener_repositorio_busquedas_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioBusquedas:
    return RepositorioBusquedasSQLAlchemy(sesion)


obtener_repositorio_busquedas: Callable[..., RepositorioBusquedas] = (
    obtener_repositorio_busquedas_sqlite if USA_SQLITE else obtener_repositorio_busquedas_en_memoria
)


@lru_cache
def obtener_repositorio_simulaciones() -> RepositorioSimulaciones:
    return RepositorioSimulacionesEnMemoria()


@lru_cache
def obtener_proveedor_trm() -> ProveedorTasaCambio:
    return ProveedorTasaCambioDatosGov(url_trm_configurada())


def obtener_listar_marcas(
    marcas: Annotated[RepositorioMarcas, Depends(obtener_repositorio_marcas)],
) -> ListarMarcas:
    return ListarMarcas(marcas)


def obtener_listar_motos(
    motos: Annotated[RepositorioMotos, Depends(obtener_repositorio_motos)],
) -> ListarMotos:
    return ListarMotos(motos)


def obtener_detalle_moto(
    motos: Annotated[RepositorioMotos, Depends(obtener_repositorio_motos)],
    tasa_cambio: Annotated[ProveedorTasaCambio, Depends(obtener_proveedor_trm)],
) -> ObtenerDetalleMoto:
    return ObtenerDetalleMoto(motos, tasa_cambio)


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
def obtener_repositorio_cotizaciones_en_memoria() -> RepositorioCotizaciones:
    return RepositorioCotizacionesEnMemoria()


def obtener_repositorio_cotizaciones_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioCotizaciones:
    return RepositorioCotizacionesSQLAlchemy(sesion)


obtener_repositorio_cotizaciones: Callable[..., RepositorioCotizaciones] = (
    obtener_repositorio_cotizaciones_sqlite
    if USA_SQLITE
    else obtener_repositorio_cotizaciones_en_memoria
)


@lru_cache
def obtener_repositorio_test_drives_en_memoria() -> RepositorioTestDrives:
    return RepositorioTestDrivesEnMemoria()


def obtener_repositorio_test_drives_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioTestDrives:
    return RepositorioTestDrivesSQLAlchemy(sesion)


obtener_repositorio_test_drives: Callable[..., RepositorioTestDrives] = (
    obtener_repositorio_test_drives_sqlite
    if USA_SQLITE
    else obtener_repositorio_test_drives_en_memoria
)


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


def obtener_listar_mis_cotizaciones(
    cotizaciones: Annotated[RepositorioCotizaciones, Depends(obtener_repositorio_cotizaciones)],
) -> ListarMisCotizaciones:
    return ListarMisCotizaciones(cotizaciones)


def obtener_listar_cola_test_drives(
    test_drives: Annotated[RepositorioTestDrives, Depends(obtener_repositorio_test_drives)],
) -> ListarColaTestDrives:
    return ListarColaTestDrives(test_drives)


def obtener_atender_siguiente_test_drive(
    test_drives: Annotated[RepositorioTestDrives, Depends(obtener_repositorio_test_drives)],
) -> AtenderSiguienteTestDrive:
    return AtenderSiguienteTestDrive(test_drives)


@lru_cache
def obtener_repositorio_accesorios_en_memoria() -> RepositorioAccesorios:
    return RepositorioAccesoriosEnMemoria()


def obtener_repositorio_accesorios_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioAccesorios:
    return RepositorioAccesoriosSQLAlchemy(sesion)


obtener_repositorio_accesorios: Callable[..., RepositorioAccesorios] = (
    obtener_repositorio_accesorios_sqlite
    if USA_SQLITE
    else obtener_repositorio_accesorios_en_memoria
)


@lru_cache
def obtener_repositorio_ubicaciones_en_memoria() -> RepositorioUbicaciones:
    return RepositorioUbicacionesEnMemoria()


def obtener_repositorio_ubicaciones_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioUbicaciones:
    return RepositorioUbicacionesSQLAlchemy(sesion)


obtener_repositorio_ubicaciones: Callable[..., RepositorioUbicaciones] = (
    obtener_repositorio_ubicaciones_sqlite
    if USA_SQLITE
    else obtener_repositorio_ubicaciones_en_memoria
)


@lru_cache
def obtener_repositorio_direcciones_en_memoria() -> RepositorioDirecciones:
    return RepositorioDireccionesEnMemoria()


def obtener_repositorio_direcciones_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioDirecciones:
    return RepositorioDireccionesSQLAlchemy(sesion)


obtener_repositorio_direcciones: Callable[..., RepositorioDirecciones] = (
    obtener_repositorio_direcciones_sqlite
    if USA_SQLITE
    else obtener_repositorio_direcciones_en_memoria
)


def obtener_listar_accesorios(
    accesorios: Annotated[RepositorioAccesorios, Depends(obtener_repositorio_accesorios)],
) -> ListarAccesorios:
    return ListarAccesorios(accesorios)


def obtener_obtener_accesorio(
    accesorios: Annotated[RepositorioAccesorios, Depends(obtener_repositorio_accesorios)],
) -> ObtenerAccesorio:
    return ObtenerAccesorio(accesorios)


def obtener_listar_departamentos(
    ubicaciones: Annotated[RepositorioUbicaciones, Depends(obtener_repositorio_ubicaciones)],
) -> ListarDepartamentos:
    return ListarDepartamentos(ubicaciones)


def obtener_obtener_departamento(
    ubicaciones: Annotated[RepositorioUbicaciones, Depends(obtener_repositorio_ubicaciones)],
) -> ObtenerDepartamento:
    return ObtenerDepartamento(ubicaciones)


def obtener_listar_municipios(
    ubicaciones: Annotated[RepositorioUbicaciones, Depends(obtener_repositorio_ubicaciones)],
) -> ListarMunicipios:
    return ListarMunicipios(ubicaciones)


def obtener_crear_direccion(
    direcciones: Annotated[RepositorioDirecciones, Depends(obtener_repositorio_direcciones)],
    ubicaciones: Annotated[RepositorioUbicaciones, Depends(obtener_repositorio_ubicaciones)],
    usuarios: Annotated[RepositorioUsuarios, Depends(obtener_repositorio_usuarios)],
) -> CrearDireccion:
    return CrearDireccion(direcciones, ubicaciones, usuarios)


def obtener_listar_direcciones_propias(
    direcciones: Annotated[RepositorioDirecciones, Depends(obtener_repositorio_direcciones)],
) -> ListarDireccionesPropias:
    return ListarDireccionesPropias(direcciones)


def obtener_obtener_direccion_propia(
    direcciones: Annotated[RepositorioDirecciones, Depends(obtener_repositorio_direcciones)],
) -> ObtenerDireccionPropia:
    return ObtenerDireccionPropia(direcciones)


@lru_cache
def obtener_repositorio_pedidos_en_memoria() -> RepositorioPedidos:
    return RepositorioPedidosEnMemoria(obtener_repositorio_accesorios_en_memoria())


def obtener_repositorio_pedidos_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioPedidos:
    return RepositorioPedidosSQLAlchemy(sesion)


obtener_repositorio_pedidos: Callable[..., RepositorioPedidos] = (
    obtener_repositorio_pedidos_sqlite if USA_SQLITE else obtener_repositorio_pedidos_en_memoria
)


@lru_cache
def obtener_repositorio_pagos_en_memoria() -> RepositorioPagos:
    return RepositorioPagosEnMemoria()


def obtener_repositorio_pagos_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioPagos:
    return RepositorioPagosSQLAlchemy(sesion)


obtener_repositorio_pagos: Callable[..., RepositorioPagos] = (
    obtener_repositorio_pagos_sqlite if USA_SQLITE else obtener_repositorio_pagos_en_memoria
)


@lru_cache
def obtener_repositorio_envios_en_memoria() -> RepositorioEnvios:
    return RepositorioEnviosEnMemoria()


def obtener_repositorio_envios_sqlite(
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> RepositorioEnvios:
    return RepositorioEnviosSQLAlchemy(sesion)


obtener_repositorio_envios: Callable[..., RepositorioEnvios] = (
    obtener_repositorio_envios_sqlite if USA_SQLITE else obtener_repositorio_envios_en_memoria
)


@lru_cache
def obtener_pasarela_pago() -> PasarelaPago:
    return PasarelaWompi(obtener_configuracion_wompi())


def obtener_expirar_reservas(
    pedidos: Annotated[RepositorioPedidos, Depends(obtener_repositorio_pedidos)],
    accesorios: Annotated[RepositorioAccesorios, Depends(obtener_repositorio_accesorios)],
    reloj: Annotated[Reloj, Depends(obtener_reloj_atencion)],
) -> ExpirarReservas:
    return ExpirarReservas(pedidos, accesorios, reloj)


class ExpirarReservasConSesionPropia:
    def __init__(self, reloj: Reloj) -> None:
        self._reloj = reloj

    def ejecutar(self) -> None:
        sesion = SessionLocal()
        try:
            ExpirarReservas(
                RepositorioPedidosSQLAlchemy(sesion),
                RepositorioAccesoriosSQLAlchemy(sesion),
                self._reloj,
            ).ejecutar()
            sesion.commit()
        except Exception:
            sesion.rollback()
            raise
        finally:
            sesion.close()


def crear_expirar_reservas() -> ExpirarReservas | ExpirarReservasConSesionPropia:
    if USA_SQLITE:
        return ExpirarReservasConSesionPropia(obtener_reloj_atencion())
    return obtener_expirar_reservas(
        obtener_repositorio_pedidos(),
        obtener_repositorio_accesorios(),
        obtener_reloj_atencion(),
    )


def obtener_confirmar_pago(
    pagos: Annotated[RepositorioPagos, Depends(obtener_repositorio_pagos)],
    pedidos: Annotated[RepositorioPedidos, Depends(obtener_repositorio_pedidos)],
    envios: Annotated[RepositorioEnvios, Depends(obtener_repositorio_envios)],
    reloj: Annotated[Reloj, Depends(obtener_reloj_atencion)],
) -> ConfirmarPago:
    return ConfirmarPago(pagos, pedidos, envios, reloj)


def obtener_crear_pedido(
    usuarios: Annotated[RepositorioUsuarios, Depends(obtener_repositorio_usuarios)],
    direcciones: Annotated[RepositorioDirecciones, Depends(obtener_repositorio_direcciones)],
    accesorios: Annotated[RepositorioAccesorios, Depends(obtener_repositorio_accesorios)],
    pedidos: Annotated[RepositorioPedidos, Depends(obtener_repositorio_pedidos)],
    pagos: Annotated[RepositorioPagos, Depends(obtener_repositorio_pagos)],
    pasarela: Annotated[PasarelaPago, Depends(obtener_pasarela_pago)],
    expirar_reservas: Annotated[ExpirarReservas, Depends(obtener_expirar_reservas)],
    reloj: Annotated[Reloj, Depends(obtener_reloj_atencion)],
) -> CrearPedido:
    return CrearPedido(
        usuarios,
        direcciones,
        accesorios,
        pedidos,
        pagos,
        pasarela,
        expirar_reservas,
        reloj,
        obtener_configuracion().minutos_reserva_pedido,
    )


def obtener_verificar_pago(
    pedidos: Annotated[RepositorioPedidos, Depends(obtener_repositorio_pedidos)],
    pagos: Annotated[RepositorioPagos, Depends(obtener_repositorio_pagos)],
    envios: Annotated[RepositorioEnvios, Depends(obtener_repositorio_envios)],
    pasarela: Annotated[PasarelaPago, Depends(obtener_pasarela_pago)],
    confirmar_pago: Annotated[ConfirmarPago, Depends(obtener_confirmar_pago)],
) -> VerificarPago:
    return VerificarPago(pedidos, pagos, envios, pasarela, confirmar_pago)


def obtener_procesar_evento_pago(
    pagos: Annotated[RepositorioPagos, Depends(obtener_repositorio_pagos)],
    pasarela: Annotated[PasarelaPago, Depends(obtener_pasarela_pago)],
    confirmar_pago: Annotated[ConfirmarPago, Depends(obtener_confirmar_pago)],
) -> ProcesarEventoPago:
    return ProcesarEventoPago(pagos, pasarela, confirmar_pago)


def obtener_listar_pedidos_propios(
    pedidos: Annotated[RepositorioPedidos, Depends(obtener_repositorio_pedidos)],
    pagos: Annotated[RepositorioPagos, Depends(obtener_repositorio_pagos)],
    envios: Annotated[RepositorioEnvios, Depends(obtener_repositorio_envios)],
    expirar_reservas: Annotated[ExpirarReservas, Depends(obtener_expirar_reservas)],
) -> ListarPedidosPropios:
    return ListarPedidosPropios(pedidos, pagos, envios, expirar_reservas)


def obtener_obtener_pedido_propio(
    pedidos: Annotated[RepositorioPedidos, Depends(obtener_repositorio_pedidos)],
    pagos: Annotated[RepositorioPagos, Depends(obtener_repositorio_pagos)],
    envios: Annotated[RepositorioEnvios, Depends(obtener_repositorio_envios)],
    expirar_reservas: Annotated[ExpirarReservas, Depends(obtener_expirar_reservas)],
) -> ObtenerPedidoPropio:
    return ObtenerPedidoPropio(pedidos, pagos, envios, expirar_reservas)


def obtener_crear_moto(
    motos: Annotated[RepositorioMotos, Depends(obtener_repositorio_motos)],
    marcas: Annotated[RepositorioMarcas, Depends(obtener_repositorio_marcas)],
) -> CrearMoto:
    return CrearMoto(motos, marcas)


def obtener_actualizar_moto(
    motos: Annotated[RepositorioMotos, Depends(obtener_repositorio_motos)],
    marcas: Annotated[RepositorioMarcas, Depends(obtener_repositorio_marcas)],
) -> ActualizarMoto:
    return ActualizarMoto(motos, marcas)


def obtener_eliminar_moto(
    motos: Annotated[RepositorioMotos, Depends(obtener_repositorio_motos)],
) -> EliminarMoto:
    return EliminarMoto(motos)


def obtener_crear_accesorio(
    accesorios: Annotated[RepositorioAccesorios, Depends(obtener_repositorio_accesorios)],
) -> CrearAccesorio:
    return CrearAccesorio(accesorios)


def obtener_actualizar_accesorio(
    accesorios: Annotated[RepositorioAccesorios, Depends(obtener_repositorio_accesorios)],
) -> ActualizarAccesorio:
    return ActualizarAccesorio(accesorios)


def obtener_eliminar_accesorio(
    accesorios: Annotated[RepositorioAccesorios, Depends(obtener_repositorio_accesorios)],
) -> EliminarAccesorio:
    return EliminarAccesorio(accesorios)


def obtener_obtener_parametros(
    parametros: Annotated[RepositorioParametros, Depends(obtener_repositorio_parametros)],
) -> ObtenerParametros:
    return ObtenerParametros(parametros)


def obtener_actualizar_parametros(
    parametros: Annotated[RepositorioParametros, Depends(obtener_repositorio_parametros)],
) -> ActualizarParametros:
    return ActualizarParametros(parametros)


def obtener_listar_pedidos_admin(
    pedidos: Annotated[RepositorioPedidos, Depends(obtener_repositorio_pedidos)],
    pagos: Annotated[RepositorioPagos, Depends(obtener_repositorio_pagos)],
    envios: Annotated[RepositorioEnvios, Depends(obtener_repositorio_envios)],
    expirar_reservas: Annotated[ExpirarReservas, Depends(obtener_expirar_reservas)],
) -> ListarPedidosAdmin:
    return ListarPedidosAdmin(pedidos, pagos, envios, expirar_reservas)


def obtener_avanzar_envio(
    envios: Annotated[RepositorioEnvios, Depends(obtener_repositorio_envios)],
    reloj: Annotated[Reloj, Depends(obtener_reloj_atencion)],
) -> AvanzarEnvio:
    return AvanzarEnvio(envios, reloj)
