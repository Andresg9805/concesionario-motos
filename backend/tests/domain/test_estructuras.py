import random

import pytest

from app.domain.catalogo import PlanCredito
from app.domain.estructuras.arbol_motos import ArbolMotosPorPrecio
from app.domain.estructuras.nodos import Nodo
from app.domain.estructuras.pila_simulaciones import PilaSimulaciones
from tests.domain import fabricas


def plan(plazo: int) -> PlanCredito:
    return PlanCredito(
        precio_cop=10_000_000, cuota_inicial_cop=0, plazo_meses=plazo, tasa_mensual=0.02
    )


def test_nodo_guarda_valor_y_siguiente():
    primero = Nodo(1)
    primero.siguiente = Nodo(2)
    assert primero.valor == 1
    assert primero.siguiente.valor == 2
    assert primero.siguiente.siguiente is None


def test_pila_nueva_esta_vacia():
    pila = PilaSimulaciones()
    assert pila.esta_vacia()
    assert pila.tamano() == 0


def test_pila_saca_primero_lo_ultimo_que_entro():
    pila = PilaSimulaciones()
    for plazo in (12, 24, 36):
        pila.apilar(plan(plazo))
    assert pila.tamano() == 3
    assert pila.desapilar().plazo_meses == 36
    assert pila.desapilar().plazo_meses == 24
    assert pila.desapilar().plazo_meses == 12
    assert pila.esta_vacia()


def test_ver_cima_no_saca_el_elemento():
    pila = PilaSimulaciones()
    pila.apilar(plan(12))
    assert pila.ver_cima().plazo_meses == 12
    assert pila.tamano() == 1


def test_desapilar_pila_vacia_da_error():
    with pytest.raises(IndexError):
        PilaSimulaciones().desapilar()


def test_ver_cima_de_pila_vacia_da_error():
    with pytest.raises(IndexError):
        PilaSimulaciones().ver_cima()


def arbol_con(precios: list[int]) -> ArbolMotosPorPrecio:
    arbol = ArbolMotosPorPrecio()
    for precio in precios:
        arbol.insertar(fabricas.moto(precio_cop=precio))
    return arbol


def precios(motos) -> list[int]:
    return [moto.precio_cop for moto in motos]


def test_arbol_vacio():
    arbol = ArbolMotosPorPrecio()
    assert arbol.esta_vacio()
    assert arbol.inorden() == []
    assert arbol.buscar_rango(0, 100_000_000) == []


def test_inorden_devuelve_de_la_mas_barata_a_la_mas_cara():
    arbol = arbol_con([20_000_000, 8_000_000, 35_000_000, 12_000_000, 25_000_000])
    assert precios(arbol.inorden()) == [
        8_000_000,
        12_000_000,
        20_000_000,
        25_000_000,
        35_000_000,
    ]
    assert arbol.tamano() == 5


def test_buscar_rango_incluye_los_limites():
    arbol = arbol_con([20_000_000, 8_000_000, 35_000_000, 12_000_000, 25_000_000])
    assert precios(arbol.buscar_rango(12_000_000, 25_000_000)) == [
        12_000_000,
        20_000_000,
        25_000_000,
    ]


def test_buscar_rango_sin_resultados():
    arbol = arbol_con([20_000_000, 8_000_000])
    assert arbol.buscar_rango(9_000_000, 19_000_000) == []


def test_rango_al_reves_no_devuelve_nada():
    arbol = arbol_con([20_000_000])
    assert arbol.buscar_rango(30_000_000, 10_000_000) == []


def test_motos_con_el_mismo_precio_se_guardan_todas():
    arbol = arbol_con([15_000_000, 15_000_000, 15_000_000])
    assert precios(arbol.buscar_rango(15_000_000, 15_000_000)) == [15_000_000] * 3


def test_buscar_rango_coincide_con_revisar_todas_las_motos():
    generador = random.Random(7)
    lista = [generador.randrange(5_000_000, 80_000_000, 500_000) for _ in range(200)]
    arbol = arbol_con(lista)
    for _ in range(50):
        a, b = sorted(generador.sample(range(0, 90_000_000, 250_000), 2))
        esperado = sorted(precio for precio in lista if a <= precio <= b)
        assert precios(arbol.buscar_rango(a, b)) == esperado
