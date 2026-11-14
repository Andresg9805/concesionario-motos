class DominioError(Exception):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class EntidadNoEncontradaError(DominioError):
    pass


class MotoNoDisponibleError(DominioError):
    pass


class CreditoInvalidoError(DominioError):
    pass


class TestDriveInvalidoError(DominioError):
    pass


class SinAsesorDisponibleError(DominioError):
    pass


class TransicionInvalidaError(DominioError):
    pass


class StockInsuficienteError(DominioError):
    pass


class PedidoInvalidoError(DominioError):
    pass


class ReservaVencidaError(DominioError):
    pass


class PagoInvalidoError(DominioError):
    pass


class FirmaInvalidaError(DominioError):
    pass


class CorreoYaRegistradoError(DominioError):
    pass


class CredencialesInvalidasError(DominioError):
    pass


class TokenInvalidoError(DominioError):
    pass
