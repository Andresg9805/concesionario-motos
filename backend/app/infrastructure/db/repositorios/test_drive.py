from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.atencion import (
    Cliente,
    EstadoTestDrive,
    Rol,
    TestDrive,
    Usuario,
)
from app.domain.catalogo import (
    CategoriaLicencia,
    Marca,
    Moto,
    TipoMoto,
)
from app.domain.puertos import RepositorioTestDrives
from app.infrastructure.models.cliente import Cliente as ClienteModelo
from app.infrastructure.models.marca import Marca as MarcaModelo
from app.infrastructure.models.moto import Moto as MotoModelo
from app.infrastructure.models.test_drive import TestDrive as TestDriveModelo
from app.infrastructure.models.usuario import Usuario as UsuarioModelo

ESTADOS_TEST_DRIVE_ABIERTOS = (
    EstadoTestDrive.PENDIENTE.value,
    EstadoTestDrive.PROGRAMADO.value,
)


class RepositorioTestDrivesSQLAlchemy(RepositorioTestDrives):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    @staticmethod
    def _marca_a_dominio(marca: MarcaModelo) -> Marca:
        return Marca(
            id=marca.id,
            nombre=marca.nombre,
            color_hex=marca.color_hex,
            descripcion=marca.descripcion or "",
        )

    @classmethod
    def _usuario_a_dominio(cls, usuario: UsuarioModelo) -> Usuario:
        marca = None
        if usuario.marca_especialidad is not None:
            marca = cls._marca_a_dominio(usuario.marca_especialidad)

        return Usuario(
            id=usuario.id,
            nombre=usuario.nombre,
            correo=usuario.correo,
            telefono=usuario.telefono,
            hash_contrasena=usuario.hash_contrasena,
            rol=Rol(usuario.rol),
            marca_especialidad=marca,
        )

    @classmethod
    def _cliente_a_dominio(cls, cliente: ClienteModelo) -> Cliente:
        return Cliente(
            id=cliente.id,
            nombre=cliente.nombre,
            correo=cliente.correo,
            telefono=cliente.telefono,
        )

    @classmethod
    def _moto_a_dominio(cls, moto: MotoModelo) -> Moto:
        return Moto(
            id=moto.id,
            marca=cls._marca_a_dominio(moto.marca),
            modelo=moto.modelo,
            anio=moto.anio,
            cilindraje_cc=moto.cilindraje_cc,
            tipo=TipoMoto(moto.tipo),
            categoria_licencia=CategoriaLicencia(moto.categoria_licencia),
            precio_cop=moto.precio_cop,
            stock=moto.stock,
            consumo_km_galon=moto.consumo_km_galon,
            costo_mantenimiento_km_cop=moto.costo_mantenimiento_km_cop,
            descripcion=moto.descripcion or "",
            imagen_url=moto.imagen_url or "",
        )

    @classmethod
    def _a_dominio(cls, modelo: TestDriveModelo) -> TestDrive:
        return TestDrive(
            id=modelo.id,
            codigo_seguimiento=modelo.codigo_seguimiento,
            cliente=cls._cliente_a_dominio(modelo.cliente),
            moto=cls._moto_a_dominio(modelo.moto),
            asesor=cls._usuario_a_dominio(modelo.asesor),
            fecha_solicitud=modelo.fecha_solicitud,
            fecha_programada=modelo.fecha_programada,
            estado=EstadoTestDrive(modelo.estado),
        )

    def guardar(self, test_drive: TestDrive) -> TestDrive:
        if test_drive.cliente.id is None:
            raise ValueError("El cliente debe estar guardado")
        if test_drive.moto.id is None:
            raise ValueError("La moto debe estar guardada")
        if test_drive.asesor.id is None:
            raise ValueError("El asesor debe estar guardado")

        cliente = self.sesion.get(ClienteModelo, test_drive.cliente.id)
        moto = self.sesion.get(MotoModelo, test_drive.moto.id)
        asesor = self.sesion.get(UsuarioModelo, test_drive.asesor.id)

        if cliente is None:
            raise ValueError("El cliente no existe")
        if moto is None:
            raise ValueError("La moto no existe")
        if asesor is None:
            raise ValueError("El asesor no existe")

        existente = self.sesion.scalar(
            select(TestDriveModelo).where(
                TestDriveModelo.codigo_seguimiento
                == test_drive.codigo_seguimiento
            )
        )

        if existente is not None and existente.id != test_drive.id:
            raise ValueError("Ya existe un test drive con ese código")

        if test_drive.id is None:
            modelo = TestDriveModelo()
            self.sesion.add(modelo)
        else:
            modelo = self.sesion.get(TestDriveModelo, test_drive.id)
            if modelo is None:
                raise ValueError("El test drive que intenta actualizar no existe")

        modelo.codigo_seguimiento = test_drive.codigo_seguimiento
        modelo.cliente_id = cliente.id
        modelo.moto_id = moto.id
        modelo.asesor_id = asesor.id
        modelo.fecha_solicitud = test_drive.fecha_solicitud
        modelo.fecha_programada = test_drive.fecha_programada
        modelo.estado = test_drive.estado.value

        self.sesion.flush()

        test_drive.id = modelo.id
        return self._a_dominio(modelo)

    def buscar_por_codigo(self, codigo: str) -> TestDrive | None:
        modelo = self.sesion.scalar(
            select(TestDriveModelo).where(
                TestDriveModelo.codigo_seguimiento == codigo
            )
        )

        return None if modelo is None else self._a_dominio(modelo)

    def listar_pendientes(self, asesor_id: int) -> list[TestDrive]:
        modelos = self.sesion.scalars(
            select(TestDriveModelo)
            .where(
                TestDriveModelo.asesor_id == asesor_id,
                TestDriveModelo.estado == EstadoTestDrive.PENDIENTE.value,
            )
            .order_by(
                TestDriveModelo.fecha_solicitud,
                TestDriveModelo.id,
            )
        ).all()

        return [self._a_dominio(modelo) for modelo in modelos]

    def contar_abiertos_por_asesor(self, marca_id: int) -> dict[int, int]:
        resultados = self.sesion.execute(
            select(
                TestDriveModelo.asesor_id,
                func.count(TestDriveModelo.id),
            )
            .join(
                UsuarioModelo,
                UsuarioModelo.id == TestDriveModelo.asesor_id,
            )
            .where(
                UsuarioModelo.marca_especialidad_id == marca_id,
                TestDriveModelo.estado.in_(ESTADOS_TEST_DRIVE_ABIERTOS),
            )
            .group_by(TestDriveModelo.asesor_id)
        ).all()

        return {
            asesor_id: cantidad
            for asesor_id, cantidad in resultados
        }
