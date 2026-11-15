from datetime import datetime, timedelta

import pytest

from app.domain.atencion import (
    Cliente,
    EstadoTestDrive,
    Rol,
    Usuario,
)
from app.domain.atencion import (
    TestDrive as DominioTestDrive,
)
from app.domain.catalogo import (
    CategoriaLicencia,
    Marca,
    Moto,
    TipoMoto,
)
from app.infrastructure.db.repositorios.test_drive import (
    RepositorioTestDrivesSQLAlchemy,
)
from tests.bd.datos import crear_marca, crear_moto, crear_usuario


@pytest.fixture
def datos(sesion):
    marca = crear_marca(sesion, "Honda")
    moto = crear_moto(sesion, marca)
    asesor = crear_usuario(
        sesion, "Carlos Gómez", "carlos@candela.com", "3001234567", "ASESOR", marca
    )
    usuario = crear_usuario(sesion, "Ana Pérez", "ana@candela.com", "3007654321", "CLIENTE")
    return {
        "marca": marca,
        "moto": moto,
        "asesor": asesor,
        "usuario": usuario,
        "cliente": usuario.persona,
    }


@pytest.fixture
def repositorio(sesion):
    return RepositorioTestDrivesSQLAlchemy(sesion)


def crear_test_drive(datos, codigo="CM-T123"):
    marca = Marca(
        id=datos["marca"].id,
        nombre="Honda",
        color_hex="#CC0000",
        descripcion="Motocicletas Honda",
    )

    moto = Moto(
        id=datos["moto"].id,
        marca=marca,
        modelo="CB 190R",
        anio=2026,
        cilindraje_cc=184,
        tipo=TipoMoto.NAKED,
        categoria_licencia=CategoriaLicencia.A2,
        precio_cop=12000000,
        stock=5,
        consumo_km_galon=120.0,
        costo_mantenimiento_km_cop=50,
        descripcion="Moto urbana",
        imagen_url="https://ejemplo.com/cb190r.jpg",
    )

    asesor = Usuario(
        id=datos["asesor"].id,
        nombre="Carlos Gómez",
        correo="carlos@candela.com",
        telefono="3001234567",
        hash_contrasena="hash",
        rol=Rol.ASESOR,
        marca_especialidad=marca,
    )

    cliente = Cliente(
        id=datos["cliente"].id,
        nombre="Ana Pérez",
        correo="ana@candela.com",
        telefono="3007654321",
    )

    fecha_solicitud = datetime(2026, 11, 15, 10, 0)

    return DominioTestDrive(
        codigo_seguimiento=codigo,
        cliente=cliente,
        moto=moto,
        asesor=asesor,
        fecha_solicitud=fecha_solicitud,
    )


def test_guardar_test_drive(repositorio, datos):
    test_drive = crear_test_drive(datos)

    resultado = repositorio.guardar(test_drive)

    assert resultado.id is not None
    assert resultado.codigo_seguimiento == "CM-T123"
    assert resultado.estado == EstadoTestDrive.PENDIENTE
    assert resultado.fecha_programada is None


def test_buscar_por_codigo(repositorio, datos):
    repositorio.guardar(crear_test_drive(datos))

    resultado = repositorio.buscar_por_codigo("CM-T123")

    assert resultado is not None
    assert resultado.codigo_seguimiento == "CM-T123"


def test_buscar_por_codigo_inexistente(repositorio):
    assert repositorio.buscar_por_codigo("CM-Z999") is None


def test_actualizar_test_drive(repositorio, datos):
    guardado = repositorio.guardar(crear_test_drive(datos))

    guardado.programar(guardado.fecha_solicitud + timedelta(days=1))

    resultado = repositorio.guardar(guardado)

    assert resultado.estado == EstadoTestDrive.PROGRAMADO
    assert resultado.fecha_programada is not None


def test_listar_pendientes(repositorio, datos):
    repositorio.guardar(crear_test_drive(datos))

    resultado = repositorio.listar_pendientes(datos["asesor"].id)

    assert len(resultado) == 1
    assert resultado[0].codigo_seguimiento == "CM-T123"


def test_no_listar_test_drives_de_otro_asesor(repositorio, datos):
    repositorio.guardar(crear_test_drive(datos))

    resultado = repositorio.listar_pendientes(9999)

    assert resultado == []


def test_no_listar_test_drive_realizado_como_pendiente(repositorio, datos):
    test_drive = crear_test_drive(datos)
    repositorio.guardar(test_drive)

    test_drive.programar(test_drive.fecha_solicitud + timedelta(days=1))
    test_drive.marcar_realizado()
    repositorio.guardar(test_drive)

    resultado = repositorio.listar_pendientes(datos["asesor"].id)

    assert resultado == []


def test_no_listar_test_drive_cancelado_como_pendiente(repositorio, datos):
    test_drive = crear_test_drive(datos)
    repositorio.guardar(test_drive)

    test_drive.cancelar()
    repositorio.guardar(test_drive)

    resultado = repositorio.listar_pendientes(datos["asesor"].id)

    assert resultado == []


def test_contar_abiertos_por_asesor(repositorio, datos):
    repositorio.guardar(crear_test_drive(datos))

    resultado = repositorio.contar_abiertos_por_asesor(datos["marca"].id)

    assert resultado == {datos["asesor"].id: 1}


def test_no_contar_test_drives_realizados(repositorio, datos):
    test_drive = crear_test_drive(datos)
    repositorio.guardar(test_drive)

    test_drive.programar(test_drive.fecha_solicitud + timedelta(days=1))
    test_drive.marcar_realizado()
    repositorio.guardar(test_drive)

    resultado = repositorio.contar_abiertos_por_asesor(datos["marca"].id)

    assert resultado == {}


def test_no_contar_test_drives_cancelados(repositorio, datos):
    test_drive = crear_test_drive(datos)
    repositorio.guardar(test_drive)

    test_drive.cancelar()
    repositorio.guardar(test_drive)

    resultado = repositorio.contar_abiertos_por_asesor(datos["marca"].id)

    assert resultado == {}


def test_guardar_sin_cliente_persistido(repositorio, datos):
    test_drive = crear_test_drive(datos)
    test_drive.cliente.id = None

    with pytest.raises(ValueError, match="cliente"):
        repositorio.guardar(test_drive)


def test_guardar_con_moto_inexistente(repositorio, datos):
    test_drive = crear_test_drive(datos)
    test_drive.moto.id = 9999

    with pytest.raises(ValueError, match="moto"):
        repositorio.guardar(test_drive)


def test_guardar_con_asesor_inexistente(repositorio, datos):
    test_drive = crear_test_drive(datos)
    test_drive.asesor.id = 9999

    with pytest.raises(ValueError, match="asesor"):
        repositorio.guardar(test_drive)
