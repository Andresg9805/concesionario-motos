from dataclasses import replace
from itertools import count
from threading import Lock

from app.domain.catalogo import Busqueda, Marca, Moto, PlanCredito
from app.domain.costo_real import ParametrosCosto
from app.domain.estructuras.pila_simulaciones import PilaSimulaciones
from app.domain.puertos import (
    FiltrosMoto,
    RepositorioBusquedas,
    RepositorioMarcas,
    RepositorioMotos,
    RepositorioParametros,
    RepositorioSimulaciones,
)
from app.infrastructure.memoria.datos_prueba import (
    marcas_iniciales,
    motos_iniciales,
    parametros_iniciales,
)


def _cumple(moto: Moto, filtros: FiltrosMoto) -> bool:
    return (
        (filtros.marca_id is None or moto.marca.id == filtros.marca_id)
        and (filtros.tipo is None or moto.tipo == filtros.tipo)
        and (
            filtros.categoria_licencia is None
            or moto.categoria_licencia == filtros.categoria_licencia
        )
        and (filtros.precio_min is None or moto.precio_cop >= filtros.precio_min)
        and (filtros.precio_max is None or moto.precio_cop <= filtros.precio_max)
        and (filtros.cilindraje_min is None or moto.cilindraje_cc >= filtros.cilindraje_min)
        and (filtros.cilindraje_max is None or moto.cilindraje_cc <= filtros.cilindraje_max)
    )


class RepositorioMarcasEnMemoria(RepositorioMarcas):
    def __init__(self, marcas: list[Marca] | None = None) -> None:
        iniciales = marcas_iniciales() if marcas is None else marcas
        self._marcas = {marca.id: marca for marca in iniciales if marca.id is not None}

    def listar(self) -> list[Marca]:
        return list(self._marcas.values())

    def buscar_por_id(self, id: int) -> Marca | None:
        return self._marcas.get(id)


class RepositorioMotosEnMemoria(RepositorioMotos):
    def __init__(self, motos: list[Moto] | None = None) -> None:
        iniciales = motos_iniciales() if motos is None else motos
        self._motos: dict[int, Moto] = {}
        self._candado = Lock()
        siguiente = max((moto.id or 0 for moto in iniciales), default=0) + 1
        self._ids = count(siguiente)
        for moto in iniciales:
            self.guardar(moto)

    def listar(self, filtros: FiltrosMoto) -> list[Moto]:
        with self._candado:
            return [moto for moto in self._motos.values() if _cumple(moto, filtros)]

    def buscar_por_id(self, id: int) -> Moto | None:
        with self._candado:
            return self._motos.get(id)

    def guardar(self, moto: Moto) -> Moto:
        with self._candado:
            identificador = moto.id if moto.id is not None else next(self._ids)
            guardada = replace(moto, id=identificador)
            self._motos[identificador] = guardada
            return guardada

    def eliminar(self, id: int) -> None:
        with self._candado:
            self._motos.pop(id, None)


class RepositorioParametrosEnMemoria(RepositorioParametros):
    def __init__(self, parametros: ParametrosCosto | None = None) -> None:
        self._parametros = parametros_iniciales() if parametros is None else parametros

    def obtener(self) -> ParametrosCosto:
        return self._parametros

    def guardar(self, parametros: ParametrosCosto) -> ParametrosCosto:
        self._parametros = parametros
        return parametros


class RepositorioBusquedasEnMemoria(RepositorioBusquedas):
    def __init__(self) -> None:
        self._busquedas: list[Busqueda] = []
        self._ids = count(1)
        self._candado = Lock()

    def guardar(self, busqueda: Busqueda) -> Busqueda:
        with self._candado:
            guardada = replace(busqueda, id=next(self._ids))
            self._busquedas.append(guardada)
            return guardada

    def listar(self) -> list[Busqueda]:
        with self._candado:
            return list(self._busquedas)


class RepositorioSimulacionesEnMemoria(RepositorioSimulaciones):
    def __init__(self) -> None:
        self._pilas: dict[str, PilaSimulaciones] = {}
        self._candado = Lock()

    def apilar(self, sesion_id: str, plan: PlanCredito) -> int:
        with self._candado:
            pila = self._pilas.setdefault(sesion_id, PilaSimulaciones())
            pila.apilar(plan)
            return pila.tamano()

    def ultima(self, sesion_id: str) -> PlanCredito | None:
        with self._candado:
            pila = self._pilas.get(sesion_id)
            if pila is None or pila.esta_vacia():
                return None
            return pila.ver_cima()

    def cantidad(self, sesion_id: str) -> int:
        with self._candado:
            pila = self._pilas.get(sesion_id)
            return 0 if pila is None else pila.tamano()
