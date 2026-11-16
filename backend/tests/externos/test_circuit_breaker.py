import asyncio

import pytest

from app.infrastructure.externos.circuit_breaker import (
    CircuitBreaker,
    EstadoCircuito,
    RespaldoNoDisponibleError,
)


class RelojFalso:
    def __init__(self):
        self.ahora = 1000.0

    def __call__(self):
        return self.ahora

    def avanzar(self, segundos):
        self.ahora += segundos


class Origen:
    def __init__(self, *resultados):
        self.resultados = list(resultados)
        self.llamadas = 0

    async def __call__(self):
        self.llamadas += 1
        resultado = self.resultados.pop(0)
        if isinstance(resultado, Exception):
            raise resultado
        return resultado


@pytest.fixture
def reloj():
    return RelojFalso()


@pytest.fixture
def circuito(reloj):
    return CircuitBreaker[float](maximo_fallos=3, segundos_apertura=60.0, reloj=reloj)


def ejecutar(circuito, origen):
    return asyncio.run(circuito.ejecutar(origen))


def abrir(circuito, origen):
    for _ in range(3):
        ejecutar(circuito, origen)


def test_estado_inicial_cerrado_deja_pasar_y_guarda_el_valor(circuito):
    origen = Origen(4000.0)
    assert circuito.estado == EstadoCircuito.CERRADO
    assert ejecutar(circuito, origen) == 4000.0
    assert circuito.ultimo_valor == 4000.0
    assert origen.llamadas == 1


def test_un_fallo_con_respaldo_devuelve_el_ultimo_valor_y_cuenta(circuito):
    origen = Origen(4000.0, RuntimeError("caído"))
    ejecutar(circuito, origen)
    assert ejecutar(circuito, origen) == 4000.0
    assert circuito.fallos_consecutivos == 1
    assert circuito.estado == EstadoCircuito.CERRADO


def test_un_exito_reinicia_el_contador(circuito):
    origen = Origen(4000.0, RuntimeError("a"), RuntimeError("b"), 4100.0)
    for _ in range(3):
        ejecutar(circuito, origen)
    assert circuito.fallos_consecutivos == 2
    assert ejecutar(circuito, origen) == 4100.0
    assert circuito.fallos_consecutivos == 0


def test_tres_fallos_seguidos_abren_el_circuito(circuito):
    origen = Origen(4000.0, *[RuntimeError("caído")] * 3)
    ejecutar(circuito, origen)
    abrir(circuito, origen)
    assert circuito.estado == EstadoCircuito.ABIERTO


def test_abierto_no_invoca_el_origen_y_devuelve_el_ultimo_valor(circuito):
    origen = Origen(4000.0, *[RuntimeError("caído")] * 3)
    ejecutar(circuito, origen)
    abrir(circuito, origen)
    llamadas = origen.llamadas
    assert ejecutar(circuito, origen) == 4000.0
    assert origen.llamadas == llamadas


def test_sin_valor_de_respaldo_lanza_error(circuito):
    origen = Origen(*[RuntimeError("caído")] * 3)
    with pytest.raises(RespaldoNoDisponibleError):
        ejecutar(circuito, origen)
    assert circuito.fallos_consecutivos == 1


def test_antes_de_60_segundos_sigue_abierto(circuito, reloj):
    origen = Origen(4000.0, *[RuntimeError("caído")] * 3)
    ejecutar(circuito, origen)
    abrir(circuito, origen)
    reloj.avanzar(59.9)
    assert circuito.estado == EstadoCircuito.ABIERTO


def test_a_los_60_segundos_pasa_a_semiabierto(circuito, reloj):
    origen = Origen(4000.0, *[RuntimeError("caído")] * 3)
    ejecutar(circuito, origen)
    abrir(circuito, origen)
    reloj.avanzar(60)
    assert circuito.estado == EstadoCircuito.SEMIABIERTO


def test_semiabierto_con_exito_vuelve_a_cerrado(circuito, reloj):
    origen = Origen(4000.0, *[RuntimeError("caído")] * 3, 4200.0)
    ejecutar(circuito, origen)
    abrir(circuito, origen)
    reloj.avanzar(60)
    assert ejecutar(circuito, origen) == 4200.0
    assert circuito.estado == EstadoCircuito.CERRADO
    assert circuito.fallos_consecutivos == 0
    assert circuito.ultimo_valor == 4200.0


def test_semiabierto_con_fallo_vuelve_a_abierto_y_reinicia_el_temporizador(circuito, reloj):
    origen = Origen(4000.0, *[RuntimeError("caído")] * 4)
    ejecutar(circuito, origen)
    abrir(circuito, origen)
    reloj.avanzar(60)
    assert ejecutar(circuito, origen) == 4000.0
    assert circuito.estado == EstadoCircuito.ABIERTO
    reloj.avanzar(59)
    assert circuito.estado == EstadoCircuito.ABIERTO
    reloj.avanzar(1)
    assert circuito.estado == EstadoCircuito.SEMIABIERTO


def test_semiabierto_permite_una_sola_llamada_de_prueba(circuito, reloj):
    origen = Origen(4000.0, *[RuntimeError("caído")] * 3, 4200.0)
    ejecutar(circuito, origen)
    abrir(circuito, origen)
    reloj.avanzar(60)

    async def dos_llamadas():
        liberar = asyncio.Event()

        async def lenta():
            await liberar.wait()
            return 4200.0

        primera = asyncio.create_task(circuito.ejecutar(lenta))
        await asyncio.sleep(0)
        segunda = await circuito.ejecutar(origen)
        liberar.set()
        return await primera, segunda

    primera, segunda = asyncio.run(dos_llamadas())
    assert primera == 4200.0
    assert segunda == 4000.0
    assert circuito.estado == EstadoCircuito.CERRADO


def test_cancelacion_no_cuenta_como_fallo(circuito):
    async def cancelada():
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(circuito.ejecutar(cancelada))
    assert circuito.fallos_consecutivos == 0
