import hashlib
import hmac
import json
from collections.abc import Callable
from typing import Any
from urllib import error, parse, request

from app.config import ConfiguracionWompi
from app.domain.excepciones import (
    EventoIgnoradoError,
    FirmaInvalidaError,
    PagoInvalidoError,
    PasarelaNoDisponibleError,
)
from app.domain.pagos_envios import EstadoPago, Pago, ResultadoPago
from app.domain.puertos import PasarelaPago

MONEDA = "COP"
EVENTO_TRANSACCION = "transaction.updated"
SEGUNDOS_ESPERA = 10

ESTADOS_WOMPI: dict[str, EstadoPago] = {
    "APPROVED": EstadoPago.APROBADO,
    "DECLINED": EstadoPago.RECHAZADO,
    "VOIDED": EstadoPago.RECHAZADO,
    "ERROR": EstadoPago.ERROR,
    "PENDING": EstadoPago.PENDIENTE,
}

ConsultaHttp = Callable[[str], dict[str, Any]]


def calcular_firma_integridad(referencia: str, monto_centavos: int, secreto_integridad: str) -> str:
    cadena = f"{referencia}{monto_centavos}{MONEDA}{secreto_integridad}"
    return hashlib.sha256(cadena.encode()).hexdigest()


def consultar_wompi_por_http(url: str) -> dict[str, Any]:
    peticion = request.Request(url, headers={"Accept": "application/json"})
    try:
        with request.urlopen(peticion, timeout=SEGUNDOS_ESPERA) as respuesta:
            cuerpo = json.load(respuesta)
    except error.HTTPError as fallo:
        if fallo.code == 404:
            raise PagoInvalidoError("Wompi no reconoce la transacción indicada") from fallo
        raise PasarelaNoDisponibleError("Wompi no pudo atender la consulta") from fallo
    except (error.URLError, TimeoutError, json.JSONDecodeError) as fallo:
        raise PasarelaNoDisponibleError("No fue posible comunicarse con Wompi") from fallo
    if not isinstance(cuerpo, dict):
        raise PasarelaNoDisponibleError("Wompi respondió con un formato inesperado")
    return cuerpo


def extraer_valor(datos: Any, ruta: str) -> Any:
    actual = datos
    for clave in ruta.split("."):
        if not isinstance(actual, dict) or clave not in actual:
            raise FirmaInvalidaError("El evento no contiene las propiedades firmadas")
        actual = actual[clave]
    return actual


def resultado_desde_transaccion(transaccion: Any) -> ResultadoPago:
    if not isinstance(transaccion, dict):
        raise PagoInvalidoError("La transacción de Wompi no tiene el formato esperado")
    try:
        estado_wompi = str(transaccion["status"]).upper()
        referencia = str(transaccion["reference"])
        monto_centavos = int(transaccion["amount_in_cents"])
        identificador = str(transaccion["id"])
    except (KeyError, TypeError, ValueError) as fallo:
        raise PagoInvalidoError("La transacción de Wompi está incompleta") from fallo
    if transaccion.get("currency", MONEDA) != MONEDA:
        raise PagoInvalidoError("La transacción no está en pesos colombianos")
    if monto_centavos % 100 != 0:
        raise PagoInvalidoError("El monto de la transacción no es válido")
    estado = ESTADOS_WOMPI.get(estado_wompi)
    if estado is None:
        raise PagoInvalidoError(f"Estado de transacción desconocido: {estado_wompi}")
    return ResultadoPago(
        referencia=referencia,
        transaccion_id=identificador,
        estado=estado,
        monto_cop=monto_centavos // 100,
    )


class PasarelaWompi(PasarelaPago):
    def __init__(
        self,
        configuracion: ConfiguracionWompi,
        consulta_http: ConsultaHttp = consultar_wompi_por_http,
    ) -> None:
        self._configuracion = configuracion
        self._consulta_http = consulta_http

    def datos_para_widget(self, pago: Pago) -> dict[str, Any]:
        monto_centavos = pago.monto_en_centavos()
        return {
            "llave_publica": self._configuracion.llave_publica,
            "referencia": pago.referencia,
            "monto_centavos": monto_centavos,
            "moneda": MONEDA,
            "firma_integridad": calcular_firma_integridad(
                pago.referencia, monto_centavos, self._configuracion.secreto_integridad
            ),
        }

    def checksum_esperado(self, cuerpo: dict[str, Any]) -> str:
        firma = cuerpo.get("signature")
        propiedades = firma.get("properties") if isinstance(firma, dict) else None
        if not isinstance(propiedades, list) or not propiedades:
            raise FirmaInvalidaError("El evento no trae firma")
        datos = cuerpo.get("data")
        valores = "".join(str(extraer_valor(datos, str(ruta))) for ruta in propiedades)
        marca_de_tiempo = cuerpo.get("timestamp")
        if marca_de_tiempo is None:
            raise FirmaInvalidaError("El evento no trae marca de tiempo")
        cadena = f"{valores}{marca_de_tiempo}{self._configuracion.secreto_eventos}"
        return hashlib.sha256(cadena.encode()).hexdigest()

    def leer_evento(self, cuerpo: dict[str, Any]) -> ResultadoPago:
        firma = cuerpo.get("signature")
        recibido = firma.get("checksum") if isinstance(firma, dict) else None
        if not isinstance(recibido, str):
            raise FirmaInvalidaError("El evento no trae checksum")
        if not hmac.compare_digest(self.checksum_esperado(cuerpo).lower(), recibido.lower()):
            raise FirmaInvalidaError("El checksum del evento no es válido")
        if cuerpo.get("event") != EVENTO_TRANSACCION:
            raise EventoIgnoradoError("El tipo de evento no se procesa")
        datos = cuerpo.get("data")
        transaccion = datos.get("transaction") if isinstance(datos, dict) else None
        return resultado_desde_transaccion(transaccion)

    def consultar_transaccion(self, transaccion_id: str) -> ResultadoPago:
        url = f"{self._configuracion.api_url}/transactions/{parse.quote(transaccion_id, safe='')}"
        respuesta = self._consulta_http(url)
        return resultado_desde_transaccion(respuesta.get("data"))
