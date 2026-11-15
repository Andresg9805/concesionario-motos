
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.atencion import Rol, Usuario
from app.domain.catalogo import Marca
from app.infrastructure.db.base import Base
from app.infrastructure.db.repositorios.usuario import (
    RepositorioUsuariosSQLAlchemy,
)
from app.infrastructure.models.marca import Marca as MarcaModelo
from app.infrastructure.models.usuario import Usuario as UsuarioModelo


@pytest.fixture
def sesion():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)
    SesionLocal = sessionmaker(bind=engine, autoflush=False)

    with SesionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def datos(sesion):
    marca = MarcaModelo(
        nombre="Honda",
        color_hex="#CC0000",
        descripcion="Motocicletas Honda",
    )
    otra_marca = MarcaModelo(
        nombre="Yamaha",
        color_hex="#0000FF",
        descripcion="Motocicletas Yamaha",
    )

    sesion.add_all([marca, otra_marca])
    sesion.flush()

    asesor = UsuarioModelo(
        nombre="Carlos Gómez",
        correo="carlos@candela.com",
        telefono="3001234567",
        hash_contrasena="hash",
        rol="ASESOR",
        marca_especialidad_id=marca.id,
    )

    otro_asesor = UsuarioModelo(
        nombre="Pedro López",
        correo="pedro@candela.com",
        telefono="3001111111",
        hash_contrasena="hash",
        rol="ASESOR",
        marca_especialidad_id=otra_marca.id,
    )

    cliente = UsuarioModelo(
        nombre="Ana Pérez",
        correo="ana@candela.com",
        telefono="3007654321",
        hash_contrasena="hash",
        rol="CLIENTE",
    )

    sesion.add_all([asesor, otro_asesor, cliente])
    sesion.flush()

    return {
        "marca": marca,
        "otra_marca": otra_marca,
        "asesor": asesor,
        "otro_asesor": otro_asesor,
        "cliente": cliente,
    }


@pytest.fixture
def repositorio(sesion):
    return RepositorioUsuariosSQLAlchemy(sesion)


def crear_usuario(marca):
    return Usuario(
        nombre="Laura Gómez",
        correo="laura@candela.com",
        telefono="3001234567",
        hash_contrasena="hash",
        rol=Rol.ASESOR,
        marca_especialidad=marca,
    )


def test_guardar_usuario_nuevo(repositorio, datos):
    usuario = crear_usuario(
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

    assert all(
        usuario.marca_especialidad.id == datos["marca"].id
        for usuario in resultado
    )


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
