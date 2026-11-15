import unicodedata
from dataclasses import replace
from itertools import count
from threading import Lock

from app.domain.puertos import (
    RepositorioAccesorios,
    RepositorioDirecciones,
    RepositorioUbicaciones,
)
from app.domain.tienda import (
    Accesorio,
    CategoriaAccesorio,
    Departamento,
    Direccion,
    Municipio,
)
from app.infrastructure.memoria.datos_prueba import accesorios_iniciales
from app.infrastructure.memoria.datos_ubicaciones import (
    departamentos_iniciales,
    municipios_iniciales,
)


def clave_alfabetica(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c)).casefold()


class RepositorioAccesoriosEnMemoria(RepositorioAccesorios):
    def __init__(self, accesorios: list[Accesorio] | None = None) -> None:
        iniciales = accesorios_iniciales() if accesorios is None else accesorios
        self._accesorios: dict[int, Accesorio] = {}
        self._candado = Lock()
        self._ids = count(max((accesorio.id or 0 for accesorio in iniciales), default=0) + 1)
        for accesorio in iniciales:
            self.guardar(accesorio)

    def listar(self, categoria: CategoriaAccesorio | None = None) -> list[Accesorio]:
        with self._candado:
            return [
                accesorio
                for accesorio in self._accesorios.values()
                if categoria is None or accesorio.categoria == categoria
            ]

    def buscar_por_id(self, id: int) -> Accesorio | None:
        with self._candado:
            return self._accesorios.get(id)

    def guardar(self, accesorio: Accesorio) -> Accesorio:
        with self._candado:
            identificador = accesorio.id if accesorio.id is not None else next(self._ids)
            guardado = replace(accesorio, id=identificador)
            self._accesorios[identificador] = guardado
            return guardado

    def eliminar(self, id: int) -> None:
        with self._candado:
            self._accesorios.pop(id, None)


class RepositorioUbicacionesEnMemoria(RepositorioUbicaciones):
    def __init__(
        self,
        departamentos: list[Departamento] | None = None,
        municipios: list[Municipio] | None = None,
    ) -> None:
        self._departamentos = departamentos_iniciales() if departamentos is None else departamentos
        self._municipios = {
            municipio.codigo: municipio
            for municipio in (municipios_iniciales() if municipios is None else municipios)
        }

    def listar_departamentos(self) -> list[Departamento]:
        return sorted(self._departamentos, key=lambda d: clave_alfabetica(d.nombre))

    def listar_municipios(self, departamento_codigo: str) -> list[Municipio]:
        return sorted(
            (
                municipio
                for municipio in self._municipios.values()
                if municipio.departamento.codigo == departamento_codigo
            ),
            key=lambda m: clave_alfabetica(m.nombre),
        )

    def buscar_municipio(self, codigo: str) -> Municipio | None:
        return self._municipios.get(codigo)


class RepositorioDireccionesEnMemoria(RepositorioDirecciones):
    def __init__(self) -> None:
        self._direcciones: dict[int, Direccion] = {}
        self._ids = count(1)
        self._candado = Lock()

    def guardar(self, direccion: Direccion) -> Direccion:
        with self._candado:
            identificador = direccion.id if direccion.id is not None else next(self._ids)
            guardada = replace(direccion, id=identificador)
            self._direcciones[identificador] = guardada
            return guardada

    def buscar_por_id(self, id: int) -> Direccion | None:
        with self._candado:
            return self._direcciones.get(id)

    def listar_por_usuario(self, usuario_id: int) -> list[Direccion]:
        with self._candado:
            return [
                direccion
                for direccion in self._direcciones.values()
                if direccion.usuario.id == usuario_id
            ]
