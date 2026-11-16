import pytest

from app.domain.tienda import Accesorio, CategoriaAccesorio, Direccion
from app.infrastructure.db.repositorios.conversiones import usuario_a_dominio
from app.infrastructure.db.repositorios.tienda import (
    RepositorioAccesoriosSQLAlchemy,
    RepositorioDireccionesSQLAlchemy,
    RepositorioUbicacionesSQLAlchemy,
)
from app.infrastructure.models import Fabricante
from tests.bd.datos import crear_accesorio, crear_ubicacion, crear_usuario


@pytest.fixture
def accesorios(sesion):
    return RepositorioAccesoriosSQLAlchemy(sesion)


def test_listar_accesorios_con_categoria_y_fabricante(sesion, accesorios):
    crear_accesorio(sesion)
    crear_accesorio(
        sesion,
        sku="ALP-GUA-001",
        nombre="Guantes Techdura",
        categoria="GUANTES",
        fabricante="Alpinestars",
        precio_cop=350_000,
    )

    lista = accesorios.listar()

    assert [(a.nombre, a.categoria, a.fabricante) for a in lista] == [
        ("X-Fifteen", CategoriaAccesorio.CASCO, "SHOEI"),
        ("Guantes Techdura", CategoriaAccesorio.GUANTES, "Alpinestars"),
    ]


def test_filtrar_accesorios_por_categoria(sesion, accesorios):
    crear_accesorio(sesion)
    crear_accesorio(sesion, sku="ALP-GUA-001", nombre="Guantes", categoria="GUANTES")

    lista = accesorios.listar(CategoriaAccesorio.GUANTES)

    assert [a.nombre for a in lista] == ["Guantes"]


def test_buscar_accesorio_que_no_existe(accesorios):
    assert accesorios.buscar_por_id(99) is None


def test_guardar_accesorio_nuevo_con_fabricante_nuevo(sesion, accesorios):
    guardado = accesorios.guardar(
        Accesorio(
            sku="LS2-CAS-001",
            nombre="Rapid II",
            categoria=CategoriaAccesorio.CASCO,
            fabricante="LS2",
            precio_cop=450_000,
            stock=3,
        )
    )

    assert guardado.id is not None
    assert guardado.fabricante == "LS2"
    assert sesion.query(Fabricante).filter_by(nombre="LS2").count() == 1


def test_actualizar_stock_de_un_accesorio(sesion, accesorios):
    modelo = crear_accesorio(sesion, stock=5)
    accesorio = accesorios.buscar_por_id(modelo.id)
    assert accesorio is not None

    accesorio.reservar(2)
    accesorios.guardar(accesorio)

    actualizado = accesorios.buscar_por_id(modelo.id)
    assert actualizado is not None
    assert actualizado.stock == 3


def test_eliminar_accesorio(sesion, accesorios):
    modelo = crear_accesorio(sesion)
    accesorios.eliminar(modelo.id)
    assert accesorios.buscar_por_id(modelo.id) is None


def test_ubicaciones(sesion):
    crear_ubicacion(sesion)
    ubicaciones = RepositorioUbicacionesSQLAlchemy(sesion)

    assert [d.nombre for d in ubicaciones.listar_departamentos()] == ["Bogotá D.C."]
    assert [m.nombre for m in ubicaciones.listar_municipios("11")] == ["Bogotá"]
    municipio = ubicaciones.buscar_municipio("11001")
    assert municipio is not None
    assert municipio.departamento.costo_envio_cop == 12_000
    assert ubicaciones.buscar_municipio("99999") is None


def test_guardar_y_listar_direcciones_del_usuario(sesion):
    municipio = crear_ubicacion(sesion)
    cliente = crear_usuario(sesion, "Ana Pérez", "ana@correo.com", "3001234567", "CLIENTE")
    ubicaciones = RepositorioUbicacionesSQLAlchemy(sesion)
    direcciones = RepositorioDireccionesSQLAlchemy(sesion)
    municipio_dominio = ubicaciones.buscar_municipio(municipio.codigo)
    assert municipio_dominio is not None

    guardada = direcciones.guardar(
        Direccion(
            usuario=usuario_a_dominio(cliente),
            municipio=municipio_dominio,
            detalle="Calle 10 # 5-20",
            telefono_contacto="3001234567",
            nombre_recibe="Ana Pérez",
        )
    )

    assert guardada.id is not None
    assert [d.detalle for d in direcciones.listar_por_usuario(cliente.id)] == ["Calle 10 # 5-20"]
    encontrada = direcciones.buscar_por_id(guardada.id)
    assert encontrada is not None
    assert encontrada.nombre_recibe == "Ana Pérez"
    assert encontrada.usuario.correo == "ana@correo.com"
