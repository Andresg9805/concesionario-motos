from app.domain.puertos import (
    FiltrosMoto,
    MotorReportes,
    RepositorioBusquedas,
    RepositorioMotos,
    RepositorioParametros,
    RepositorioPedidos,
)
from app.domain.reportes import FilaRadar, ReporteVentas
from app.domain.tienda import EstadoPedido


class GenerarRadarDemanda:
    def __init__(
        self,
        busquedas: RepositorioBusquedas,
        motos: RepositorioMotos,
        parametros: RepositorioParametros,
        motor: MotorReportes,
    ) -> None:
        self._busquedas = busquedas
        self._motos = motos
        self._parametros = parametros
        self._motor = motor

    def ejecutar(self) -> list[FilaRadar]:
        return self._motor.radar_demanda(
            self._busquedas.listar(),
            self._motos.listar(FiltrosMoto()),
            self._parametros.obtener().tasa_mensual,
        )


class GenerarReporteVentas:
    def __init__(self, pedidos: RepositorioPedidos, motor: MotorReportes) -> None:
        self._pedidos = pedidos
        self._motor = motor

    def ejecutar(self) -> ReporteVentas:
        pagados = [p for p in self._pedidos.listar() if p.estado == EstadoPedido.PAGADO]
        return self._motor.ventas_accesorios(pagados)
