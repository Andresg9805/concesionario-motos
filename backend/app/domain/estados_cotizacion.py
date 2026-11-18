from abc import ABC, abstractmethod
from enum import StrEnum

from app.domain.excepciones import TransicionInvalidaError


class EstadoAtencion(StrEnum):
    NUEVO = "NUEVO"
    CONTACTADO = "CONTACTADO"
    TEST_DRIVE = "TEST_DRIVE"
    NEGOCIANDO = "NEGOCIANDO"
    VENDIDO = "VENDIDO"
    DESCARTADO = "DESCARTADO"


class EstadoDeCotizacion(ABC):
    clave: EstadoAtencion

    @abstractmethod
    def siguientes(self) -> frozenset[EstadoAtencion]: ...

    @abstractmethod
    def mensaje_para_cliente(self) -> str: ...

    def esta_abierta(self) -> bool:
        return True

    def pasar_a(self, nuevo: EstadoAtencion) -> "EstadoDeCotizacion":
        if nuevo not in self.siguientes():
            raise TransicionInvalidaError(
                f"No se puede pasar de {self.clave.value} a {nuevo.value}"
            )
        return estado_de(nuevo)


class EstadoCerrado(EstadoDeCotizacion):
    def siguientes(self) -> frozenset[EstadoAtencion]:
        return frozenset()

    def esta_abierta(self) -> bool:
        return False


class Nuevo(EstadoDeCotizacion):
    clave = EstadoAtencion.NUEVO

    def siguientes(self) -> frozenset[EstadoAtencion]:
        return frozenset({EstadoAtencion.CONTACTADO, EstadoAtencion.DESCARTADO})

    def mensaje_para_cliente(self) -> str:
        return "Recibimos tu solicitud. Tu asesor te va a contactar pronto."


class Contactado(EstadoDeCotizacion):
    clave = EstadoAtencion.CONTACTADO

    def siguientes(self) -> frozenset[EstadoAtencion]:
        return frozenset(
            {EstadoAtencion.TEST_DRIVE, EstadoAtencion.NEGOCIANDO, EstadoAtencion.DESCARTADO}
        )

    def mensaje_para_cliente(self) -> str:
        return "Tu asesor ya se comunicó contigo."


class EnTestDrive(EstadoDeCotizacion):
    clave = EstadoAtencion.TEST_DRIVE

    def siguientes(self) -> frozenset[EstadoAtencion]:
        return frozenset({EstadoAtencion.NEGOCIANDO, EstadoAtencion.DESCARTADO})

    def mensaje_para_cliente(self) -> str:
        return "Estás probando la moto con tu asesor."


class Negociando(EstadoDeCotizacion):
    clave = EstadoAtencion.NEGOCIANDO

    def siguientes(self) -> frozenset[EstadoAtencion]:
        return frozenset({EstadoAtencion.VENDIDO, EstadoAtencion.DESCARTADO})

    def mensaje_para_cliente(self) -> str:
        return "Estás negociando el precio y la financiación con tu asesor."


class Vendido(EstadoCerrado):
    clave = EstadoAtencion.VENDIDO

    def mensaje_para_cliente(self) -> str:
        return "¡Felicitaciones! La moto ya es tuya."


class Descartado(EstadoCerrado):
    clave = EstadoAtencion.DESCARTADO

    def mensaje_para_cliente(self) -> str:
        return "Esta cotización se cerró sin compra."


ESTADOS: dict[EstadoAtencion, EstadoDeCotizacion] = {
    estado.clave: estado
    for estado in (Nuevo(), Contactado(), EnTestDrive(), Negociando(), Vendido(), Descartado())
}


def estado_de(clave: EstadoAtencion) -> EstadoDeCotizacion:
    return ESTADOS[clave]


ESTADOS_CERRADOS: frozenset[EstadoAtencion] = frozenset(
    clave for clave, estado in ESTADOS.items() if not estado.esta_abierta()
)
