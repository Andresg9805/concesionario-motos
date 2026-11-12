import inspect

import pytest

from app.domain import puertos
from app.domain.puertos import FiltrosMoto, RepositorioMotos
from tests.domain import fabricas


def clases_de_puertos():
    return [
        clase
        for _, clase in inspect.getmembers(puertos, inspect.isclass)
        if clase.__module__ == puertos.__name__ and inspect.isabstract(clase)
    ]


def test_hay_17_puertos():
    assert len(clases_de_puertos()) == 17


@pytest.mark.parametrize("puerto", clases_de_puertos(), ids=lambda clase: clase.__name__)
def test_un_puerto_no_se_puede_instanciar(puerto):
    with pytest.raises(TypeError):
        puerto()


class RepositorioMotosEnMemoria(RepositorioMotos):
    def __init__(self):
        self.motos = {}

    def listar(self, filtros):
        return [
            moto
            for moto in self.motos.values()
            if filtros.precio_max is None or moto.precio_cop <= filtros.precio_max
        ]

    def buscar_por_id(self, id):
        return self.motos.get(id)

    def guardar(self, moto):
        self.motos[moto.id] = moto
        return moto

    def eliminar(self, id):
        self.motos.pop(id, None)


def test_una_implementacion_cumple_el_puerto():
    repositorio = RepositorioMotosEnMemoria()
    repositorio.guardar(fabricas.moto())
    assert repositorio.buscar_por_id(1) is not None
    assert repositorio.listar(FiltrosMoto(precio_max=1_000)) == []
    repositorio.eliminar(1)
    assert repositorio.buscar_por_id(1) is None
