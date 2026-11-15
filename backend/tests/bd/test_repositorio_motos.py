import pytest

from app.domain.catalogo import CategoriaLicencia, Marca, Moto, TipoMoto
from app.domain.puertos import FiltrosMoto
from app.infrastructure.db.repositorios.marca import RepositorioMarcasSQLAlchemy
from app.infrastructure.db.repositorios.moto import RepositorioMotosSQLAlchemy
from tests.bd.datos import crear_marca, crear_moto


@pytest.fixture
def datos(sesion):
    honda = crear_marca(sesion, "Honda")
    yamaha = crear_marca(sesion, "Yamaha", "#0033A0")
    moto = crear_moto(sesion, honda)
    return {"honda": honda, "yamaha": yamaha, "moto": moto}


def test_listar_marcas(sesion, datos):
    repositorio = RepositorioMarcasSQLAlchemy(sesion)

    marcas = repositorio.listar()

    assert len(marcas) == 2
    assert [marca.nombre for marca in marcas] == ["Honda", "Yamaha"]


def test_buscar_marca_por_id(sesion, datos):
    repositorio = RepositorioMarcasSQLAlchemy(sesion)

    marca = repositorio.buscar_por_id(datos["honda"].id)

    assert marca is not None
    assert marca.nombre == "Honda"


def test_buscar_marca_inexistente(sesion):
    repositorio = RepositorioMarcasSQLAlchemy(sesion)

    assert repositorio.buscar_por_id(999) is None


def test_listar_motos(sesion, datos):
    repositorio = RepositorioMotosSQLAlchemy(sesion)

    motos = repositorio.listar(FiltrosMoto())

    assert len(motos) == 1
    assert motos[0].modelo == "CB 190R"
    assert motos[0].marca.nombre == "Honda"


def test_filtrar_motos_por_marca(sesion, datos):
    repositorio = RepositorioMotosSQLAlchemy(sesion)

    filtros = FiltrosMoto(marca_id=datos["honda"].id)
    motos = repositorio.listar(filtros)

    assert len(motos) == 1
    assert motos[0].marca.nombre == "Honda"


def test_filtrar_motos_por_precio(sesion, datos):
    repositorio = RepositorioMotosSQLAlchemy(sesion)

    filtros = FiltrosMoto(precio_min=10000000, precio_max=13000000)
    motos = repositorio.listar(filtros)

    assert len(motos) == 1


def test_filtrar_motos_sin_resultados(sesion, datos):
    repositorio = RepositorioMotosSQLAlchemy(sesion)

    filtros = FiltrosMoto(precio_min=20000000)
    assert repositorio.listar(filtros) == []


def test_buscar_moto_por_id(sesion, datos):
    repositorio = RepositorioMotosSQLAlchemy(sesion)

    moto = repositorio.buscar_por_id(datos["moto"].id)

    assert moto is not None
    assert moto.modelo == "CB 190R"
    assert moto.marca.nombre == "Honda"


def test_buscar_moto_inexistente(sesion):
    repositorio = RepositorioMotosSQLAlchemy(sesion)

    assert repositorio.buscar_por_id(999) is None


def test_guardar_moto_nueva(sesion, datos):
    repositorio = RepositorioMotosSQLAlchemy(sesion)
    marca = RepositorioMarcasSQLAlchemy(sesion).buscar_por_id(datos["yamaha"].id)
    assert marca is not None

    moto = Moto(
        marca=marca,
        modelo="MT-03",
        anio=2025,
        cilindraje_cc=321,
        tipo=TipoMoto.NAKED,
        categoria_licencia=CategoriaLicencia.A2,
        precio_cop=30000000,
        stock=3,
        consumo_km_galon=110.0,
        costo_mantenimiento_km_cop=60,
    )

    guardada = repositorio.guardar(moto)

    assert guardada.id is not None
    assert guardada.modelo == "MT-03"
    assert guardada.marca.nombre == "Yamaha"


def test_actualizar_moto(sesion, datos):
    repositorio = RepositorioMotosSQLAlchemy(sesion)
    moto = repositorio.buscar_por_id(datos["moto"].id)

    moto.stock = 8
    moto.precio_cop = 12500000

    actualizada = repositorio.guardar(moto)

    assert actualizada.stock == 8
    assert actualizada.precio_cop == 12500000


def test_eliminar_moto(sesion, datos):
    repositorio = RepositorioMotosSQLAlchemy(sesion)
    moto_id = datos["moto"].id

    repositorio.eliminar(moto_id)

    assert repositorio.buscar_por_id(moto_id) is None


def test_guardar_moto_con_marca_inexistente(sesion):
    repositorio = RepositorioMotosSQLAlchemy(sesion)
    marca = Marca(
        id=999,
        nombre="Honda",
        color_hex="#CC0000",
    )
    moto = Moto(
        marca=marca,
        modelo="CB 190R",
        anio=2025,
        cilindraje_cc=184,
        tipo=TipoMoto.NAKED,
        categoria_licencia=CategoriaLicencia.A2,
        precio_cop=12000000,
        stock=5,
        consumo_km_galon=120.0,
        costo_mantenimiento_km_cop=50,
    )

    with pytest.raises(ValueError):
        repositorio.guardar(moto)
