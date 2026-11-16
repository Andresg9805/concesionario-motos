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
from app.config import obtener_configuracion, obtener_configuracion_wompi
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
from app.infrastructure.memoria.datos_prueba import asesores_iniciales
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


@lru_cache
def obtener_repositorio_accesorios() -> RepositorioAccesorios:
    return RepositorioAccesoriosEnMemoria()


@lru_cache
def obtener_repositorio_ubicaciones() -> RepositorioUbicaciones:
    return RepositorioUbicacionesEnMemoria()


@lru_cache
def obtener_repositorio_direcciones() -> RepositorioDirecciones:
    return RepositorioDireccionesEnMemoria()


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
def obtener_repositorio_pedidos() -> RepositorioPedidos:
    return RepositorioPedidosEnMemoria(obtener_repositorio_accesorios())


@lru_cache
def obtener_repositorio_pagos() -> RepositorioPagos:
    return RepositorioPagosEnMemoria()


@lru_cache
def obtener_repositorio_envios() -> RepositorioEnvios:
    return RepositorioEnviosEnMemoria()


@lru_cache
def obtener_pasarela_pago() -> PasarelaPago:
    return PasarelaWompi(obtener_configuracion_wompi())


def obtener_expirar_reservas(
    pedidos: Annotated[RepositorioPedidos, Depends(obtener_repositorio_pedidos)],
    accesorios: Annotated[RepositorioAccesorios, Depends(obtener_repositorio_accesorios)],
    reloj: Annotated[Reloj, Depends(obtener_reloj_atencion)],
) -> ExpirarReservas:
    return ExpirarReservas(pedidos, accesorios, reloj)


def crear_expirar_reservas() -> ExpirarReservas:
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
