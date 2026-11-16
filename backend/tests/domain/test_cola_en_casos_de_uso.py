from dataclasses import replace
from datetime import timedelta

import pytest

from app.application.atencion import (
    AtenderSiguienteTestDrive,
    ListarColaTestDrives,
    cola_del_asesor,
)
from app.domain.atencion import EstadoTestDrive, TestDrive
from app.domain.excepciones import EntidadNoEncontradaError
from app.domain.puertos import RepositorioTestDrives
from tests.domain import fabricas

AHORA = fabricas.AHORA


class RepositorioFalso(RepositorioTestDrives):
    def __init__(self, pendientes: list[TestDrive]) -> None:
        self.pendientes = pendientes
        self.guardados: list[TestDrive] = []

    def guardar(self, test_drive: TestDrive) -> TestDrive:
        self.guardados.append(test_drive)
        return test_drive

    def buscar_por_codigo(self, codigo: str) -> TestDrive | None:
        return None

    def listar_pendientes(self, asesor_id: int) -> list[TestDrive]:
        return list(self.pendientes)

    def contar_abiertos_por_asesor(self, marca_id: int) -> dict[int, int]:
        return {}


def pendientes(*codigos: str) -> list[TestDrive]:
    return [replace(fabricas.test_drive(), codigo_seguimiento=codigo) for codigo in codigos]


def test_la_cola_del_asesor_respeta_el_orden_de_llegada():
    repositorio = RepositorioFalso(pendientes("CM-AAAA", "CM-BBBB", "CM-CCCC"))

    cola = cola_del_asesor(repositorio, asesor_id=1)

    assert len(cola) == 3
    assert [t.codigo_seguimiento for t in cola] == ["CM-AAAA", "CM-BBBB", "CM-CCCC"]


def test_listar_la_cola_devuelve_los_pendientes_en_orden():
    repositorio = RepositorioFalso(pendientes("CM-AAAA", "CM-BBBB"))

    lista = ListarColaTestDrives(repositorio).ejecutar(asesor_id=1)

    assert [t.codigo_seguimiento for t in lista] == ["CM-AAAA", "CM-BBBB"]


def test_atender_siguiente_programa_el_primero_de_la_cola():
    repositorio = RepositorioFalso(pendientes("CM-AAAA", "CM-BBBB"))
    fecha = AHORA + timedelta(days=1)

    atendido = AtenderSiguienteTestDrive(repositorio).ejecutar(asesor_id=1, fecha=fecha)

    assert atendido.codigo_seguimiento == "CM-AAAA"
    assert atendido.estado == EstadoTestDrive.PROGRAMADO
    assert atendido.fecha_programada == fecha
    assert repositorio.guardados == [atendido]


def test_atender_siguiente_con_la_cola_vacia_lanza_error():
    with pytest.raises(EntidadNoEncontradaError):
        AtenderSiguienteTestDrive(RepositorioFalso([])).ejecutar(asesor_id=1, fecha=AHORA)
