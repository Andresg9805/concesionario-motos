
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.atencion import (
    Cliente,
    Cotizacion,
    EstadoAtencion,
    Rol,
    Usuario,
)
from app.domain.catalogo import (
    CategoriaLicencia,
    Marca,
    Moto,
    PlanCredito,
    TipoMoto,
)
from app.infrastructure.db.base import Base
from app.infrastructure.db.repositorios.cotizacion import (
    RepositorioCotizacionesSQLAlchemy,
)
from app.infrastructure.models.cliente import Cliente as ClienteModelo
from app.infrastructure.models.marca import Marca as MarcaModelo
from app.infrastructure.models.moto import Moto as MotoModelo
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
    sesion.add(marca)
    sesion.flush()

    moto = MotoModelo(
        marca_id=marca.id,
        modelo="CB 190R",
        anio=2026,
        cilindraje_cc=184,
        tipo="NAKED",
        categoria_licencia="A2",
        precio_cop=12000000,
        stock=5,
        consumo_km_galon=120.0,
        costo_mantenimiento_km_cop=50,
        descripcion="Moto urbana",
        imagen_url="https://ejemplo.com/cb190r.jpg",
    )
    sesion.add(moto)

    asesor = UsuarioModelo(
        nombre="Carlos Gómez",
        correo="carlos@candela.com",
        telefono="3001234567",
        hash_contrasena="hash",
        rol="ASESOR",
        marca_especialidad_id=marca.id,
    )

    usuario = UsuarioModelo(
        nombre="Ana Pérez",
        correo="ana@candela.com",
        telefono="3007654321",
        hash_contrasena="hash",
        rol="CLIENTE",
    )

    sesion.add_all([asesor, usuario])
    sesion.flush()

    cliente = ClienteModelo(
        nombre="Ana Pérez",
        correo="ana@candela.com",
        telefono="3007654321",
        usuario_id=usuario.id,
    )
    sesion.add(cliente)
    sesion.flush()

    return {
        "marca": marca,
        "moto": moto,
        "asesor": asesor,
        "usuario": usuario,
        "cliente": cliente,
    }


@pytest.fixture
def repositorio(sesion):
    return RepositorioCotizacionesSQLAlchemy(sesion)


def crear_cotizacion(datos, codigo="CM-A123"):
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

    plan = PlanCredito(
        precio_cop=12000000,
        cuota_inicial_cop=2000000,
        plazo_meses=36,
        tasa_mensual=0.015,
    )

    return Cotizacion(
        codigo_seguimiento=codigo,
        cliente=cliente,
        moto=moto,
        asesor=asesor,
        fecha=date(2026, 11, 15),
        plan=plan,
    )


def test_guardar_cotizacion(repositorio, datos):
    cotizacion = crear_cotizacion(datos)

    resultado = repositorio.guardar(cotizacion)

    assert resultado.id is not None
    assert resultado.codigo_seguimiento == "CM-A123"
    assert resultado.estado == EstadoAtencion.NUEVO
    assert resultado.plan.precio_cop == 12000000


def test_buscar_por_codigo(repositorio, datos):
    cotizacion = crear_cotizacion(datos)
    repositorio.guardar(cotizacion)

    resultado = repositorio.buscar_por_codigo("CM-A123")

    assert resultado is not None
    assert resultado.codigo_seguimiento == "CM-A123"


def test_buscar_por_codigo_inexistente(repositorio):
    assert repositorio.buscar_por_codigo("CM-Z999") is None


def test_buscar_por_id(repositorio, datos):
    guardada = repositorio.guardar(crear_cotizacion(datos))

    resultado = repositorio.buscar_por_id(guardada.id)

    assert resultado is not None
    assert resultado.id == guardada.id


def test_buscar_por_id_inexistente(repositorio):
    assert repositorio.buscar_por_id(9999) is None


def test_actualizar_cotizacion(repositorio, datos):
    guardada = repositorio.guardar(crear_cotizacion(datos))

    guardada.cambiar_estado(EstadoAtencion.CONTACTADO)
    resultado = repositorio.guardar(guardada)

    assert resultado.estado == EstadoAtencion.CONTACTADO


def test_listar_por_asesor(repositorio, datos):
    repositorio.guardar(crear_cotizacion(datos))

    resultado = repositorio.listar_por_asesor(datos["asesor"].id)

    assert len(resultado) == 1
    assert resultado[0].codigo_seguimiento == "CM-A123"


def test_listar_por_usuario(repositorio, datos):
    repositorio.guardar(crear_cotizacion(datos))

    resultado = repositorio.listar_por_usuario(datos["usuario"].id)

    assert len(resultado) == 1
    assert resultado[0].codigo_seguimiento == "CM-A123"


def test_contar_abiertas_por_asesor(repositorio, datos):
    repositorio.guardar(crear_cotizacion(datos))

    resultado = repositorio.contar_abiertas_por_asesor(datos["marca"].id)

    assert resultado == {datos["asesor"].id: 1}


def test_no_contar_cotizaciones_vendidas(repositorio, datos):
    cotizacion = crear_cotizacion(datos)
    repositorio.guardar(cotizacion)

    cotizacion.cambiar_estado(EstadoAtencion.CONTACTADO)
    cotizacion.cambiar_estado(EstadoAtencion.NEGOCIANDO)
    cotizacion.cambiar_estado(EstadoAtencion.VENDIDO)
    repositorio.guardar(cotizacion)

    resultado = repositorio.contar_abiertas_por_asesor(datos["marca"].id)

    assert resultado == {}


def test_no_contar_cotizaciones_descartadas(repositorio, datos):
    cotizacion = crear_cotizacion(datos)
    repositorio.guardar(cotizacion)

    cotizacion.cambiar_estado(EstadoAtencion.DESCARTADO)
    repositorio.guardar(cotizacion)

    resultado = repositorio.contar_abiertas_por_asesor(datos["marca"].id)

    assert resultado == {}


def test_guardar_sin_cliente_persistido(repositorio, datos):
    cotizacion = crear_cotizacion(datos)
    cotizacion.cliente.id = None

    with pytest.raises(ValueError, match="cliente"):
        repositorio.guardar(cotizacion)


def test_guardar_con_moto_inexistente(repositorio, datos):
    cotizacion = crear_cotizacion(datos)
    cotizacion.moto.id = 9999

    with pytest.raises(ValueError, match="moto"):
        repositorio.guardar(cotizacion)


def test_guardar_con_asesor_inexistente(repositorio, datos):
    cotizacion = crear_cotizacion(datos)
    cotizacion.asesor.id = 9999

    with pytest.raises(ValueError, match="asesor"):
        repositorio.guardar(cotizacion)
