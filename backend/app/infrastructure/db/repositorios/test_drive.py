from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.atencion import EstadoTestDrive, TestDrive
from app.domain.puertos import RepositorioTestDrives
from app.infrastructure.db.repositorios.conversiones import (
    cliente_a_dominio,
    fecha_a_bd,
    fecha_desde_bd,
    moto_a_dominio,
    usuario_a_dominio,
)
from app.infrastructure.models.asesor import Asesor as AsesorModelo
from app.infrastructure.models.moto import Moto as MotoModelo
from app.infrastructure.models.persona import Persona as PersonaModelo
from app.infrastructure.models.test_drive import TestDrive as TestDriveModelo

ESTADOS_ABIERTOS = (EstadoTestDrive.PENDIENTE.value, EstadoTestDrive.PROGRAMADO.value)


def _a_dominio(modelo: TestDriveModelo) -> TestDrive:
    return TestDrive(
        id=modelo.id,
        codigo_seguimiento=modelo.codigo_seguimiento,
        cliente=cliente_a_dominio(modelo.cliente),
        moto=moto_a_dominio(modelo.moto),
        asesor=usuario_a_dominio(modelo.asesor.usuario),
        fecha_solicitud=fecha_desde_bd(modelo.fecha_solicitud),
        fecha_programada=(
            None if modelo.fecha_programada is None else fecha_desde_bd(modelo.fecha_programada)
        ),
        estado=EstadoTestDrive(modelo.estado),
    )


class RepositorioTestDrivesSQLAlchemy(RepositorioTestDrives):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, test_drive: TestDrive) -> TestDrive:
        cliente = self.sesion.get(PersonaModelo, test_drive.cliente.id or 0)
        moto = self.sesion.get(MotoModelo, test_drive.moto.id or 0)
        asesor = self.sesion.get(AsesorModelo, test_drive.asesor.id or 0)

        if cliente is None:
            raise ValueError("El cliente no existe")
        if moto is None:
            raise ValueError("La moto no existe")
        if asesor is None:
            raise ValueError("El asesor no existe")

        mismo_codigo = self.sesion.scalar(
            select(TestDriveModelo).where(
                TestDriveModelo.codigo_seguimiento == test_drive.codigo_seguimiento
            )
        )
        if mismo_codigo is not None and mismo_codigo.id != test_drive.id:
            raise ValueError("Ya existe un test drive con ese código")

        if test_drive.id is None:
            modelo = TestDriveModelo()
            self.sesion.add(modelo)
        else:
            existente = self.sesion.get(TestDriveModelo, test_drive.id)
            if existente is None:
                raise ValueError("El test drive que intenta actualizar no existe")
            modelo = existente

        modelo.codigo_seguimiento = test_drive.codigo_seguimiento
        modelo.cliente_id = cliente.id
        modelo.moto_id = moto.id
        modelo.asesor_id = asesor.usuario_id
        modelo.fecha_solicitud = fecha_a_bd(test_drive.fecha_solicitud)
        modelo.fecha_programada = (
            None if test_drive.fecha_programada is None else fecha_a_bd(test_drive.fecha_programada)
        )
        modelo.estado = test_drive.estado.value

        self.sesion.flush()
        self.sesion.refresh(modelo)
        test_drive.id = modelo.id
        return _a_dominio(modelo)

    def buscar_por_codigo(self, codigo: str) -> TestDrive | None:
        modelo = self.sesion.scalar(
            select(TestDriveModelo).where(TestDriveModelo.codigo_seguimiento == codigo)
        )
        return None if modelo is None else _a_dominio(modelo)

    def listar_pendientes(self, asesor_id: int) -> list[TestDrive]:
        modelos = self.sesion.scalars(
            select(TestDriveModelo)
            .where(
                TestDriveModelo.asesor_id == asesor_id,
                TestDriveModelo.estado == EstadoTestDrive.PENDIENTE.value,
            )
            .order_by(TestDriveModelo.fecha_solicitud, TestDriveModelo.id)
        ).all()
        return [_a_dominio(modelo) for modelo in modelos]

    def contar_abiertos_por_asesor(self, marca_id: int) -> dict[int, int]:
        filas = self.sesion.execute(
            select(TestDriveModelo.asesor_id, func.count(TestDriveModelo.id))
            .join(TestDriveModelo.asesor)
            .where(
                AsesorModelo.marca_id == marca_id,
                TestDriveModelo.estado.in_(ESTADOS_ABIERTOS),
            )
            .group_by(TestDriveModelo.asesor_id)
        ).all()
        return {asesor_id: cantidad for asesor_id, cantidad in filas}
