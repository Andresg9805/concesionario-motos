from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status

from app.api.dependencias import (
    obtener_crear_pedido,
    obtener_listar_pedidos_propios,
    obtener_obtener_pedido_propio,
    obtener_procesar_evento_pago,
    obtener_verificar_pago,
    requerir_rol,
)
from app.api.schemas.pedidos import (
    PedidoCreadoSalida,
    PedidoDetalleSalida,
    PedidoEntrada,
    PedidoResumenSalida,
    VerificarPagoEntrada,
    VerificarPagoSalida,
    WompiSalida,
)
from app.application.pedidos import (
    CrearPedido,
    DatosItem,
    ListarPedidosPropios,
    ObtenerPedidoPropio,
    ProcesarEventoPago,
    VerificarPago,
)
from app.domain.atencion import Rol
from app.domain.excepciones import (
    EntidadNoEncontradaError,
    EventoIgnoradoError,
    FirmaInvalidaError,
    PagoInvalidoError,
    PasarelaNoDisponibleError,
    PedidoInvalidoError,
    StockInsuficienteError,
    TransicionInvalidaError,
)
from app.domain.seguridad import DatosToken

router_pedidos = APIRouter(prefix="/pedidos", tags=["Pedidos"])
router_mis_pedidos = APIRouter(prefix="/mis-pedidos", tags=["Pedidos"])
router_webhooks = APIRouter(tags=["Pagos"])

SesionCliente = Annotated[DatosToken, Depends(requerir_rol(Rol.CLIENTE))]

RESPUESTAS_PROTEGIDAS: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"description": "No autenticado"},
    status.HTTP_403_FORBIDDEN: {"description": "Solo los clientes tienen pedidos"},
}

RESPUESTA_PEDIDO_AJENO: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {"description": "El pedido no existe o es de otro cliente"},
}


@router_pedidos.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PedidoCreadoSalida,
    responses={
        **RESPUESTAS_PROTEGIDAS,
        status.HTTP_404_NOT_FOUND: {"description": "La dirección no existe o es de otro cliente"},
        status.HTTP_409_CONFLICT: {"description": "Un accesorio no existe o no tiene stock"},
    },
)
def crear_pedido(
    entrada: PedidoEntrada,
    sesion: SesionCliente,
    caso_de_uso: Annotated[CrearPedido, Depends(obtener_crear_pedido)],
) -> PedidoCreadoSalida:
    try:
        creado = caso_de_uso.ejecutar(
            sesion.usuario_id,
            entrada.direccion_id,
            [DatosItem(item.accesorio_id, item.cantidad) for item in entrada.items],
        )
    except EntidadNoEncontradaError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=error.mensaje) from error
    except StockInsuficienteError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=error.mensaje) from error
    except PedidoInvalidoError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=error.mensaje) from error
    return PedidoCreadoSalida(
        pedido_id=creado.pedido.id or 0,
        total_cop=creado.pedido.total_cop(),
        reservado_hasta=creado.pedido.reservado_hasta,
        wompi=WompiSalida.desde_datos(creado.datos_widget),
    )


@router_mis_pedidos.get(
    "", response_model=list[PedidoResumenSalida], responses=RESPUESTAS_PROTEGIDAS
)
def listar_mis_pedidos(
    sesion: SesionCliente,
    caso_de_uso: Annotated[ListarPedidosPropios, Depends(obtener_listar_pedidos_propios)],
) -> list[PedidoResumenSalida]:
    return [
        PedidoResumenSalida.desde_vista(vista) for vista in caso_de_uso.ejecutar(sesion.usuario_id)
    ]


@router_mis_pedidos.get(
    "/{pedido_id}",
    response_model=PedidoDetalleSalida,
    responses={**RESPUESTAS_PROTEGIDAS, **RESPUESTA_PEDIDO_AJENO},
)
def obtener_mi_pedido(
    pedido_id: Annotated[int, Path(ge=1)],
    sesion: SesionCliente,
    caso_de_uso: Annotated[ObtenerPedidoPropio, Depends(obtener_obtener_pedido_propio)],
) -> PedidoDetalleSalida:
    try:
        vista = caso_de_uso.ejecutar(sesion.usuario_id, pedido_id)
    except EntidadNoEncontradaError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=error.mensaje) from error
    return PedidoDetalleSalida.desde_vista(vista)


@router_mis_pedidos.post(
    "/{pedido_id}/verificar-pago",
    response_model=VerificarPagoSalida,
    responses={
        **RESPUESTAS_PROTEGIDAS,
        **RESPUESTA_PEDIDO_AJENO,
        status.HTTP_409_CONFLICT: {"description": "El estado del pago no admite el cambio"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "La transacción no corresponde"},
        status.HTTP_502_BAD_GATEWAY: {"description": "Wompi no está disponible"},
    },
)
def verificar_pago(
    pedido_id: Annotated[int, Path(ge=1)],
    entrada: VerificarPagoEntrada,
    sesion: SesionCliente,
    caso_de_uso: Annotated[VerificarPago, Depends(obtener_verificar_pago)],
) -> VerificarPagoSalida:
    try:
        vista = caso_de_uso.ejecutar(sesion.usuario_id, pedido_id, entrada.transaccion_id)
    except EntidadNoEncontradaError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=error.mensaje) from error
    except TransicionInvalidaError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=error.mensaje) from error
    except PagoInvalidoError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=error.mensaje) from error
    except PasarelaNoDisponibleError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=error.mensaje) from error
    return VerificarPagoSalida.desde_vista(vista)


@router_webhooks.post(
    "/webhooks/wompi",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "El checksum del evento no es válido"},
        status.HTTP_404_NOT_FOUND: {"description": "No existe un pago con esa referencia"},
    },
)
@router_webhooks.post("/pagos/webhook", include_in_schema=False)
def recibir_evento_wompi(
    cuerpo: Annotated[dict[str, Any], Body()],
    caso_de_uso: Annotated[ProcesarEventoPago, Depends(obtener_procesar_evento_pago)],
) -> dict[str, bool]:
    try:
        procesado = caso_de_uso.ejecutar(cuerpo)
    except FirmaInvalidaError as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=error.mensaje) from error
    except EventoIgnoradoError:
        return {"procesado": False}
    except EntidadNoEncontradaError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=error.mensaje) from error
    except TransicionInvalidaError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=error.mensaje) from error
    except PagoInvalidoError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=error.mensaje) from error
    return {"procesado": procesado}
