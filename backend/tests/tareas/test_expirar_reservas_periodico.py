import asyncio
import logging

import pytest
from fastapi.testclient import TestClient

from app.api import dependencias, tareas
from app.api.tareas import INTERVALO_EXPIRAR_RESERVAS_SEGUNDOS, ciclo_expirar_reservas
from app.application.pedidos import ExpirarReservas
from app.main import app


class CasoDeUsoFalso:
    def __init__(self, fallos=()):
        self.ejecuciones = 0
        self.fallos = set(fallos)

    def ejecutar(self):
        self.ejecuciones += 1
        if self.ejecuciones in self.fallos:
            raise RuntimeError("fallo puntual")


class Reloj:
    def __init__(self, ciclos):
        self.ciclos = ciclos
        self.esperas = []

    async def __call__(self, segundos):
        if len(self.esperas) == self.ciclos:
            raise asyncio.CancelledError
        self.esperas.append(segundos)


def test_el_intervalo_por_defecto_es_de_60_segundos():
    assert INTERVALO_EXPIRAR_RESERVAS_SEGUNDOS == 60


def test_el_ciclo_ejecuta_el_caso_de_uso_despues_de_cada_espera():
    caso = CasoDeUsoFalso()
    dormir = Reloj(ciclos=3)
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(ciclo_expirar_reservas(lambda: caso, 60, dormir))
    assert dormir.esperas == [60, 60, 60]
    assert caso.ejecuciones == 3


def test_un_fallo_puntual_se_registra_y_no_detiene_el_ciclo(caplog):
    caso = CasoDeUsoFalso(fallos={2})
    dormir = Reloj(ciclos=4)
    with caplog.at_level(logging.ERROR, logger=tareas.__name__):
        with pytest.raises(asyncio.CancelledError):
            asyncio.run(ciclo_expirar_reservas(lambda: caso, 60, dormir))
    assert caso.ejecuciones == 4
    assert [r.levelno for r in caplog.records] == [logging.ERROR]
    assert caplog.records[0].exc_info is not None


def test_el_caso_de_uso_se_obtiene_desde_dependencias():
    caso = dependencias.crear_expirar_reservas()
    assert isinstance(caso, ExpirarReservas)
    assert caso._pedidos is dependencias.obtener_repositorio_pedidos()
    assert caso._accesorios is dependencias.obtener_repositorio_accesorios()


def test_el_ciclo_de_vida_lanza_la_tarea_y_la_cancela_al_apagar(monkeypatch):
    estado = {"iniciada": False, "cancelada": False}

    async def ciclo_falso(obtener_caso_de_uso):
        estado["iniciada"] = True
        assert obtener_caso_de_uso is dependencias.crear_expirar_reservas
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            estado["cancelada"] = True
            raise

    monkeypatch.setattr("app.main.ciclo_expirar_reservas", ciclo_falso)
    with TestClient(app) as cliente:
        assert cliente.get("/health").status_code == 200
        assert estado["iniciada"]
        assert not estado["cancelada"]
    assert estado["cancelada"]
