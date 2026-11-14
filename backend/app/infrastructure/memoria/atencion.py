from collections import Counter
from dataclasses import replace
from itertools import count
from threading import Lock

from app.domain.atencion import Cotizacion, EstadoTestDrive, TestDrive
from app.domain.puertos import RepositorioCotizaciones, RepositorioTestDrives

ESTADOS_TEST_DRIVE_ABIERTOS = (EstadoTestDrive.PENDIENTE, EstadoTestDrive.PROGRAMADO)


class RepositorioCotizacionesEnMemoria(RepositorioCotizaciones):
    def __init__(self) -> None:
        self._cotizaciones: dict[int, Cotizacion] = {}
        self._ids = count(1)
        self._candado = Lock()

    def guardar(self, cotizacion: Cotizacion) -> Cotizacion:
        with self._candado:
            existente = self._por_codigo(cotizacion.codigo_seguimiento)
            if existente is not None and existente.id != cotizacion.id:
                raise ValueError("Ya existe una cotización con ese código")
            identificador = cotizacion.id if cotizacion.id is not None else next(self._ids)
            guardada = replace(cotizacion, id=identificador)
            self._cotizaciones[identificador] = guardada
            return replace(guardada)

    def buscar_por_codigo(self, codigo: str) -> Cotizacion | None:
        with self._candado:
            encontrada = self._por_codigo(codigo)
            return None if encontrada is None else replace(encontrada)

    def buscar_por_id(self, id: int) -> Cotizacion | None:
        with self._candado:
            encontrada = self._cotizaciones.get(id)
            return None if encontrada is None else replace(encontrada)

    def listar_por_asesor(self, asesor_id: int) -> list[Cotizacion]:
        with self._candado:
            return [
                replace(cotizacion)
                for cotizacion in self._ordenadas()
                if cotizacion.asesor.id == asesor_id
            ]

    def listar_por_usuario(self, usuario_id: int) -> list[Cotizacion]:
        with self._candado:
            return [
                replace(cotizacion)
                for cotizacion in self._ordenadas()
                if cotizacion.cliente.usuario is not None
                and cotizacion.cliente.usuario.id == usuario_id
            ]

    def contar_abiertas_por_asesor(self, marca_id: int) -> dict[int, int]:
        with self._candado:
            return dict(
                Counter(
                    cotizacion.asesor.id
                    for cotizacion in self._cotizaciones.values()
                    if cotizacion.asesor.id is not None
                    and cotizacion.asesor.marca_especialidad is not None
                    and cotizacion.asesor.marca_especialidad.id == marca_id
                    and cotizacion.esta_abierta()
                )
            )

    def _por_codigo(self, codigo: str) -> Cotizacion | None:
        return next(
            (c for c in self._cotizaciones.values() if c.codigo_seguimiento == codigo), None
        )

    def _ordenadas(self) -> list[Cotizacion]:
        return sorted(self._cotizaciones.values(), key=lambda cotizacion: cotizacion.id or 0)


class RepositorioTestDrivesEnMemoria(RepositorioTestDrives):
    def __init__(self) -> None:
        self._test_drives: dict[int, TestDrive] = {}
        self._ids = count(1)
        self._candado = Lock()

    def guardar(self, test_drive: TestDrive) -> TestDrive:
        with self._candado:
            existente = self._por_codigo(test_drive.codigo_seguimiento)
            if existente is not None and existente.id != test_drive.id:
                raise ValueError("Ya existe un test drive con ese código")
            identificador = test_drive.id if test_drive.id is not None else next(self._ids)
            guardado = replace(test_drive, id=identificador)
            self._test_drives[identificador] = guardado
            return replace(guardado)

    def buscar_por_codigo(self, codigo: str) -> TestDrive | None:
        with self._candado:
            encontrado = self._por_codigo(codigo)
            return None if encontrado is None else replace(encontrado)

    def listar_pendientes(self, asesor_id: int) -> list[TestDrive]:
        with self._candado:
            pendientes = [
                test_drive
                for test_drive in self._test_drives.values()
                if test_drive.asesor.id == asesor_id
                and test_drive.estado == EstadoTestDrive.PENDIENTE
            ]
            pendientes.sort(key=lambda test_drive: (test_drive.fecha_solicitud, test_drive.id or 0))
            return [replace(test_drive) for test_drive in pendientes]

    def contar_abiertos_por_asesor(self, marca_id: int) -> dict[int, int]:
        with self._candado:
            return dict(
                Counter(
                    test_drive.asesor.id
                    for test_drive in self._test_drives.values()
                    if test_drive.asesor.id is not None
                    and test_drive.asesor.marca_especialidad is not None
                    and test_drive.asesor.marca_especialidad.id == marca_id
                    and test_drive.estado in ESTADOS_TEST_DRIVE_ABIERTOS
                )
            )

    def _por_codigo(self, codigo: str) -> TestDrive | None:
        return next((t for t in self._test_drives.values() if t.codigo_seguimiento == codigo), None)
