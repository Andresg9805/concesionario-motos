import pytest

from app.domain.atencion import Rol, Usuario
from app.domain.catalogo import Marca
from app.infrastructure.db.repositorios.usuario import (
    RepositorioUsuariosSQLAlchemy,
)
from tests.bd.datos import crear_marca, crear_usuario


@pytest.fixture
def datos(sesion):
    marca = crear_marca(sesion, "Honda")
    otra_marca = crear_marca(sesion, "Yamaha", "#0033A0")
    return {
        "marca": marca,
        "otra_marca": otra_marca,
        "asesor": crear_usuario(
            sesion, "Carlos Gómez", "carlos@candela.com", "3001234567", "ASESOR", marca
        ),
        "otro_asesor": crear_usuario(
            sesion, "Pedro López", "pedro@candela.com", "3001111111", "ASESOR", otra_marca
        ),
        "cliente": crear_usuario(sesion, "Ana Pérez", "ana@candela.com", "3007654321", "CLIENTE"),
    }


@pytest.fixture
def repositorio(sesion):
    return RepositorioUsuariosSQLAlchemy(sesion)


def asesor_nuevo(marca):
    return Usuario(
        nombre="Laura Gómez",
        correo="laura@candela.com",
        telefono="3001234567",
        hash_contrasena="hash",
        rol=Rol.ASESOR,
        marca_especialidad=marca,
    )


def test_guardar_usuario_nuevo(repositorio, datos):
    usuario = asesor_nuevo(
        Marca(
            id=datos["marca"].id,
            nombre="Honda",
            color_hex="#CC0000",
            descripcion="Motocicletas Honda",
        )
    )

    resultado = repositorio.guardar(usuario)

    assert resultado.id is not None
    assert resultado.correo == "laura@candela.com"
    assert resultado.rol == Rol.ASESOR
    assert resultado.marca_especialidad.id == datos["marca"].id


def test_actualizar_usuario(repositorio, datos):
    usuario = repositorio.buscar_por_id(datos["asesor"].id)

    usuario.nombre = "Carlos Gómez Actualizado"
    resultado = repositorio.guardar(usuario)

    assert resultado.nombre == "Carlos Gómez Actualizado"
    assert resultado.id == datos["asesor"].id


def test_buscar_por_correo(repositorio, datos):
    resultado = repositorio.buscar_por_correo("carlos@candela.com")

    assert resultado is not None
    assert resultado.nombre == "Carlos Gómez"
    assert resultado.rol == Rol.ASESOR


def test_buscar_por_correo_normalizado(repositorio, datos):
    resultado = repositorio.buscar_por_correo("  CARLOS@CANDELA.COM  ")

    assert resultado is not None
    assert resultado.correo == "carlos@candela.com"


def test_buscar_por_correo_inexistente(repositorio):
    assert repositorio.buscar_por_correo("noexiste@candela.com") is None


def test_buscar_por_id(repositorio, datos):
    resultado = repositorio.buscar_por_id(datos["asesor"].id)

    assert resultado is not None
    assert resultado.id == datos["asesor"].id


def test_buscar_por_id_inexistente(repositorio):
    assert repositorio.buscar_por_id(9999) is None


def test_listar_asesores_por_marca(repositorio, datos):
    resultado = repositorio.listar_asesores(datos["marca"].id)

    assert len(resultado) == 1
    assert resultado[0].correo == "carlos@candela.com"


def test_no_listar_asesores_de_otra_marca(repositorio, datos):
    resultado = repositorio.listar_asesores(datos["marca"].id)

    assert all(usuario.marca_especialidad.id == datos["marca"].id for usuario in resultado)


def test_no_listar_clientes_como_asesores(repositorio, datos):
    resultado = repositorio.listar_asesores(datos["marca"].id)

    assert all(usuario.rol == Rol.ASESOR for usuario in resultado)
    assert all(usuario.correo != "ana@candela.com" for usuario in resultado)


def test_rechazar_correo_duplicado(repositorio, datos):
    usuario = Usuario(
        nombre="Otro Carlos",
        correo="CARLOS@CANDELA.COM",
        telefono="3009999999",
        hash_contrasena="otro_hash",
        rol=Rol.ASESOR,
        marca_especialidad=Marca(
            id=datos["marca"].id,
            nombre="Honda",
            color_hex="#CC0000",
            descripcion="Motocicletas Honda",
        ),
    )

    with pytest.raises(ValueError, match="Ya existe un usuario con ese correo"):
        repositorio.guardar(usuario)
