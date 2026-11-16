from dataclasses import dataclass
from typing import TypeVar

from app.application.atencion import Reloj
from app.application.pedidos import ExpirarReservas, VistaPedido
from app.domain.catalogo import Moto, TipoMoto
from app.domain.costo_real import ParametrosCosto, TarifaSoat
from app.domain.excepciones import EntidadNoEncontradaError
from app.domain.pagos_envios import Envio, EstadoEnvio
from app.domain.puertos import (
    RepositorioAccesorios,
    RepositorioEnvios,
    RepositorioMarcas,
    RepositorioMotos,
    RepositorioPagos,
    RepositorioParametros,
    RepositorioPedidos,
)
from app.domain.tienda import Accesorio, CategoriaAccesorio

_T = TypeVar("_T")


@dataclass(frozen=True)
class DatosMoto:
    marca_id: int
    modelo: str
    anio: int
    cilindraje_cc: int
    tipo: TipoMoto
    precio_cop: int
    stock: int
    consumo_km_galon: float
    costo_mantenimiento_km_cop: int
    descripcion: str
    imagen_url: str


@dataclass(frozen=True)
class DatosAccesorio:
    sku: str
    nombre: str
    categoria: CategoriaAccesorio
    fabricante: str
    descripcion: str
    precio_cop: int
    stock: int
    imagen_url: str


@dataclass(frozen=True)
class DatosTarifaSoat:
    cilindraje_min: int
    cilindraje_max: int
    valor_anual_cop: int


@dataclass(frozen=True)
class DatosParametros:
    precio_galon_cop: int
    porcentaje_impuesto: float
    tarifas_soat: list[DatosTarifaSoat]
    valor_matricula_cop: int | None = None
    valor_tramites_cop: int | None = None
    tasa_mensual: float | None = None


def _construir_moto(marcas: RepositorioMarcas, datos: DatosMoto, id: int | None) -> Moto:
    marca = marcas.buscar_por_id(datos.marca_id)
    if marca is None:
        raise EntidadNoEncontradaError(f"No existe una marca con id {datos.marca_id}")
    return Moto(
        id=id,
        marca=marca,
        modelo=datos.modelo,
        anio=datos.anio,
        cilindraje_cc=datos.cilindraje_cc,
        tipo=datos.tipo,
        precio_cop=datos.precio_cop,
        stock=datos.stock,
        consumo_km_galon=datos.consumo_km_galon,
        costo_mantenimiento_km_cop=datos.costo_mantenimiento_km_cop,
        descripcion=datos.descripcion,
        imagen_url=datos.imagen_url,
    )


def _moto_existente(motos: RepositorioMotos, moto_id: int) -> Moto:
    moto = motos.buscar_por_id(moto_id)
    if moto is None:
        raise EntidadNoEncontradaError(f"No existe una moto con id {moto_id}")
    return moto


def _accesorio_existente(accesorios: RepositorioAccesorios, accesorio_id: int) -> Accesorio:
    accesorio = accesorios.buscar_por_id(accesorio_id)
    if accesorio is None:
        raise EntidadNoEncontradaError(f"No existe un accesorio con id {accesorio_id}")
    return accesorio


class CrearMoto:
    def __init__(self, motos: RepositorioMotos, marcas: RepositorioMarcas) -> None:
        self._motos = motos
        self._marcas = marcas

    def ejecutar(self, datos: DatosMoto) -> Moto:
        return self._motos.guardar(_construir_moto(self._marcas, datos, None))


class ActualizarMoto:
    def __init__(self, motos: RepositorioMotos, marcas: RepositorioMarcas) -> None:
        self._motos = motos
        self._marcas = marcas

    def ejecutar(self, moto_id: int, datos: DatosMoto) -> Moto:
        _moto_existente(self._motos, moto_id)
        return self._motos.guardar(_construir_moto(self._marcas, datos, moto_id))


class EliminarMoto:
    def __init__(self, motos: RepositorioMotos) -> None:
        self._motos = motos

    def ejecutar(self, moto_id: int) -> None:
        _moto_existente(self._motos, moto_id)
        self._motos.eliminar(moto_id)


def _construir_accesorio(datos: DatosAccesorio, id: int | None) -> Accesorio:
    return Accesorio(
        id=id,
        sku=datos.sku,
        nombre=datos.nombre,
        categoria=datos.categoria,
        fabricante=datos.fabricante,
        descripcion=datos.descripcion,
        precio_cop=datos.precio_cop,
        stock=datos.stock,
        imagen_url=datos.imagen_url,
    )


class CrearAccesorio:
    def __init__(self, accesorios: RepositorioAccesorios) -> None:
        self._accesorios = accesorios

    def ejecutar(self, datos: DatosAccesorio) -> Accesorio:
        return self._accesorios.guardar(_construir_accesorio(datos, None))


class ActualizarAccesorio:
    def __init__(self, accesorios: RepositorioAccesorios) -> None:
        self._accesorios = accesorios

    def ejecutar(self, accesorio_id: int, datos: DatosAccesorio) -> Accesorio:
        _accesorio_existente(self._accesorios, accesorio_id)
        return self._accesorios.guardar(_construir_accesorio(datos, accesorio_id))


class EliminarAccesorio:
    def __init__(self, accesorios: RepositorioAccesorios) -> None:
        self._accesorios = accesorios

    def ejecutar(self, accesorio_id: int) -> None:
        _accesorio_existente(self._accesorios, accesorio_id)
        self._accesorios.eliminar(accesorio_id)


class ObtenerParametros:
    def __init__(self, parametros: RepositorioParametros) -> None:
        self._parametros = parametros

    def ejecutar(self) -> ParametrosCosto:
        return self._parametros.obtener()


class ActualizarParametros:
    def __init__(self, parametros: RepositorioParametros) -> None:
        self._parametros = parametros

    def ejecutar(self, datos: DatosParametros) -> ParametrosCosto:
        actuales = self._parametros.obtener()
        nuevos = ParametrosCosto(
            id=actuales.id,
            precio_galon_cop=datos.precio_galon_cop,
            porcentaje_impuesto=datos.porcentaje_impuesto,
            tarifas_soat=[
                TarifaSoat(
                    cilindraje_min=tarifa.cilindraje_min,
                    cilindraje_max=tarifa.cilindraje_max,
                    valor_anual_cop=tarifa.valor_anual_cop,
                )
                for tarifa in datos.tarifas_soat
            ],
            valor_matricula_cop=_o_actual(datos.valor_matricula_cop, actuales.valor_matricula_cop),
            valor_tramites_cop=_o_actual(datos.valor_tramites_cop, actuales.valor_tramites_cop),
            tasa_mensual=_o_actual(datos.tasa_mensual, actuales.tasa_mensual),
        )
        return self._parametros.guardar(nuevos)


def _o_actual(nuevo: _T | None, actual: _T) -> _T:
    return actual if nuevo is None else nuevo


class ListarPedidosAdmin:
    def __init__(
        self,
        pedidos: RepositorioPedidos,
        pagos: RepositorioPagos,
        envios: RepositorioEnvios,
        expirar_reservas: ExpirarReservas,
    ) -> None:
        self._pedidos = pedidos
        self._pagos = pagos
        self._envios = envios
        self._expirar_reservas = expirar_reservas

    def ejecutar(self) -> list[VistaPedido]:
        self._expirar_reservas.ejecutar()
        todos = sorted(self._pedidos.listar(), key=lambda pedido: pedido.id or 0, reverse=True)
        return [
            VistaPedido(
                pedido=pedido,
                pago=self._pagos.buscar_por_pedido(pedido.id or 0),
                envio=self._envios.buscar_por_pedido(pedido.id or 0),
            )
            for pedido in todos
        ]


class AvanzarEnvio:
    def __init__(self, envios: RepositorioEnvios, reloj: Reloj) -> None:
        self._envios = envios
        self._reloj = reloj

    def ejecutar(self, envio_id: int, estado: EstadoEnvio, nota: str) -> Envio:
        envio = self._envios.buscar_por_id(envio_id)
        if envio is None:
            raise EntidadNoEncontradaError(f"No existe un envío con id {envio_id}")
        envio.avanzar(estado, nota, self._reloj())
        return self._envios.guardar(envio)
