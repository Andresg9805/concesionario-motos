from dataclasses import replace

import pytest

from app.domain.estructuras.cola_test_drives import (
    AgendaTestDrives,
    ColaTestDrives,
)
from tests.domain import fabricas


def test_cola_nueva_esta_vacia():
    cola = ColaTestDrives()

    assert cola.esta_vacia()
    assert len(cola) == 0
    assert list(cola) == []


def test_encolar_y_desencolar_respeta_orden_fifo():
    cola = ColaTestDrives()
    primero = replace(fabricas.test_drive(), codigo_seguimiento="CM-A1B2")
    segundo = replace(fabricas.test_drive(), codigo_seguimiento="CM-C3D4")
    tercero = replace(fabricas.test_drive(), codigo_seguimiento="CM-E5F6")

    cola.encolar(primero)
    cola.encolar(segundo)
    cola.encolar(tercero)

    assert len(cola) == 3
    assert cola.desencolar() is primero
    assert cola.desencolar() is segundo
    assert cola.desencolar() is tercero
    assert cola.esta_vacia()


def test_frente_consulta_sin_desencolar():
    cola = ColaTestDrives()
    test_drive = fabricas.test_drive()

    cola.encolar(test_drive)

    assert cola.frente() is test_drive
    assert len(cola) == 1


def test_desencolar_cola_vacia_lanza_error():
    with pytest.raises(IndexError):
        ColaTestDrives().desencolar()


def test_frente_cola_vacia_lanza_error():
    with pytest.raises(IndexError):
        ColaTestDrives().frente()


def test_iteracion_respeta_orden_de_llegada():
    cola = ColaTestDrives()
    primero = replace(fabricas.test_drive(), codigo_seguimiento="CM-A1B2")
    segundo = replace(fabricas.test_drive(), codigo_seguimiento="CM-C3D4")

    cola.encolar(primero)
    cola.encolar(segundo)

    assert list(cola) == [primero, segundo]


def test_agenda_mantiene_colas_separadas_por_asesor():
    agenda = AgendaTestDrives()
    test_drive_1 = fabricas.test_drive()
    test_drive_2 = replace(fabricas.test_drive(), codigo_seguimiento="CM-C3D4")

    agenda.encolar(1, test_drive_1)
    agenda.encolar(2, test_drive_2)

    assert agenda.siguiente(1) is test_drive_1
    assert agenda.siguiente(2) is test_drive_2


def test_pendientes_disminuye_al_atender():
    agenda = AgendaTestDrives()
    primero = fabricas.test_drive()
    segundo = replace(fabricas.test_drive(), codigo_seguimiento="CM-C3D4")

    agenda.encolar(1, primero)
    agenda.encolar(1, segundo)

    assert agenda.pendientes(1) == 2

    agenda.siguiente(1)

    assert agenda.pendientes(1) == 1


def test_siguiente_de_asesor_sin_cola_lanza_error():
    with pytest.raises(IndexError):
        AgendaTestDrives().siguiente(99)


def test_desencolar_ultimo_elemento_permite_volver_a_encolar():
    cola = ColaTestDrives()
    primero = fabricas.test_drive()
    segundo = replace(fabricas.test_drive(), codigo_seguimiento="CM-C3D4")

    cola.encolar(primero)
    assert cola.desencolar() is primero

    cola.encolar(segundo)

    assert cola.frente() is segundo
    assert cola.desencolar() is segundo
    assert cola.esta_vacia()
