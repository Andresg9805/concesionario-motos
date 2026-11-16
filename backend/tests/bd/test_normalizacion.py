import pytest
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import IntegrityError

from app.domain.atencion import Cliente, Rol, Usuario
from app.domain.catalogo import CategoriaLicencia
from app.domain.puertos import FiltrosMoto
from app.infrastructure.db.repositorios.moto import RepositorioMotosSQLAlchemy
from app.infrastructure.db.repositorios.usuario import (
    RepositorioClientesSQLAlchemy,
    RepositorioUsuariosSQLAlchemy,
)
from app.infrastructure.db.seeds.accesorios import seed_accesorios
from app.infrastructure.db.seeds.catalogos import seed_catalogos
from app.infrastructure.db.seeds.marcas import seed_marcas
from app.infrastructure.db.seeds.motos import seed_motos
from app.infrastructure.db.seeds.parametros_costo import seed_parametros_costo
from app.infrastructure.db.seeds.ubicaciones import seed_ubicaciones
from app.infrastructure.db.seeds.usuarios import seed_usuarios
from app.infrastructure.memoria.datos_prueba import ASESORES
from app.infrastructure.memoria.datos_ubicaciones import DEPARTAMENTOS, MUNICIPIOS
from app.infrastructure.models import (
    Accesorio,
    Asesor,
    CategoriaAccesorio,
    Departamento,
    Fabricante,
    Marca,
    Moto,
    Municipio,
    ParametrosCosto,
    Persona,
    TarifaSoat,
    TipoMoto,
)
from app.infrastructure.models.usuario import Usuario as UsuarioORM
from tests.bd.datos import crear_marca, crear_moto, crear_persona


def cargar_todo(sesion):
    seed_catalogos(sesion)
    seed_marcas(sesion)
    sesion.flush()

    seed_usuarios(sesion)
    seed_motos(sesion)
    seed_accesorios(sesion)
    seed_parametros_costo(sesion)
    seed_ubicaciones(sesion)

    sesion.flush()


def contar(sesion, modelo):
    return sesion.scalar(select(func.count()).select_from(modelo))


def columnas(sesion, tabla):
    return {columna["name"] for columna in inspect(sesion.get_bind()).get_columns(tabla)}


def test_la_carga_inicial_llena_el_catalogo(sesion):
    cargar_todo(sesion)

    assert contar(sesion, Marca) == 3
    assert contar(sesion, Moto) == 60
    assert contar(sesion, Accesorio) == 35
    assert contar(sesion, TipoMoto) == 4
    assert contar(sesion, CategoriaAccesorio) == 7
    assert contar(sesion, Fabricante) == 7

    assert contar(sesion, UsuarioORM) == 8
    assert contar(sesion, Asesor) == len(ASESORES)
    assert contar(sesion, UsuarioORM) == contar(sesion, Persona)

    administradores = sesion.scalar(
        select(func.count()).select_from(UsuarioORM).where(UsuarioORM.rol == "ADMIN")
    )
    assert administradores == 1

    assert contar(sesion, ParametrosCosto) == 1
    assert contar(sesion, TarifaSoat) == 3
    assert contar(sesion, Departamento) == len(DEPARTAMENTOS)
    assert contar(sesion, Municipio) == sum(len(municipios) for municipios in MUNICIPIOS.values())


def test_cargar_dos_veces_no_duplica_nada(sesion):
    cargar_todo(sesion)
    cargar_todo(sesion)

    assert contar(sesion, Marca) == 3
    assert contar(sesion, Moto) == 60
    assert contar(sesion, Accesorio) == 35
    assert contar(sesion, Fabricante) == 7

    assert contar(sesion, UsuarioORM) == 8
    assert contar(sesion, Asesor) == len(ASESORES)
    assert contar(sesion, ParametrosCosto) == 1
    assert contar(sesion, TarifaSoat) == 3
    assert contar(sesion, Departamento) == len(DEPARTAMENTOS)
    assert contar(sesion, Municipio) == sum(len(municipios) for municipios in MUNICIPIOS.values())


def test_cada_tipo_de_moto_tiene_quince_motos(sesion):
    cargar_todo(sesion)

    filas = sesion.execute(
        select(TipoMoto.clave, func.count(Moto.id)).join(Moto.tipo).group_by(TipoMoto.clave)
    ).all()

    assert dict(filas) == {
        "NAKED": 15,
        "DOBLE_PROPOSITO": 15,
        "TRAIL": 15,
        "DEPORTIVA": 15,
    }


def test_el_nombre_del_accesorio_no_repite_su_fabricante(sesion):
    cargar_todo(sesion)

    for accesorio in sesion.scalars(select(Accesorio)):
        if accesorio.categoria.clave == "MANTENIMIENTO":
            continue

        assert accesorio.fabricante.nombre.lower() not in accesorio.nombre.lower()


def test_no_se_puede_repetir_una_marca(sesion):
    crear_marca(sesion, "Honda")

    with pytest.raises(IntegrityError):
        crear_marca(sesion, "Honda")


def test_no_se_puede_repetir_una_moto_de_la_misma_marca_y_anio(sesion):
    honda = crear_marca(sesion, "Honda")
    crear_moto(sesion, honda)

    with pytest.raises(IntegrityError):
        crear_moto(sesion, honda)


def test_no_se_puede_repetir_el_correo_de_una_persona(sesion):
    crear_persona(sesion, "Ana Pérez", "ana@correo.com", "3001234567")

    with pytest.raises(IntegrityError):
        crear_persona(sesion, "Ana María", "ana@correo.com", "3009999999")


def test_la_licencia_se_calcula_con_el_cilindraje(sesion):
    honda = crear_marca(sesion, "Honda")
    crear_moto(sesion, honda, modelo="Navi", cilindraje_cc=110)
    crear_moto(sesion, honda, modelo="XR190L", cilindraje_cc=184)

    repositorio = RepositorioMotosSQLAlchemy(sesion)

    a1 = repositorio.listar(FiltrosMoto(categoria_licencia=CategoriaLicencia.A1))
    a2 = repositorio.listar(FiltrosMoto(categoria_licencia=CategoriaLicencia.A2))

    assert [(m.modelo, m.categoria_licencia) for m in a1] == [("Navi", CategoriaLicencia.A1)]
    assert [(m.modelo, m.categoria_licencia) for m in a2] == [("XR190L", CategoriaLicencia.A2)]


def test_un_cliente_que_luego_crea_cuenta_queda_como_una_sola_persona(sesion):
    clientes = RepositorioClientesSQLAlchemy(sesion)
    usuarios = RepositorioUsuariosSQLAlchemy(sesion)

    cliente = clientes.guardar(
        Cliente(
            nombre="Ana Pérez",
            correo="ana@correo.com",
            telefono="3001234567",
        )
    )

    usuario = usuarios.guardar(
        Usuario(
            nombre="Ana Pérez",
            correo="ANA@correo.com",
            telefono="3001234567",
            hash_contrasena="hash",
            rol=Rol.CLIENTE,
        )
    )

    assert contar(sesion, Persona) == 1

    encontrado = clientes.buscar_por_correo("ana@correo.com")

    assert encontrado is not None
    assert encontrado.id == cliente.id
    assert encontrado.usuario is not None
    assert encontrado.usuario.id == usuario.id


@pytest.mark.parametrize(
    ("tabla", "columna"),
    [
        ("motos", "categoria_licencia"),
        ("motos", "tipo"),
        ("cotizaciones", "cuota_mensual_cop"),
        ("pedidos", "subtotal_cop"),
        ("pedidos", "total_cop"),
        ("envios", "costo_cop"),
        ("envios", "estado"),
        ("usuarios", "nombre"),
        ("usuarios", "correo"),
        ("usuarios", "telefono"),
        ("usuarios", "marca_especialidad_id"),
        ("accesorios", "categoria"),
    ],
)
def test_no_se_guardan_datos_que_se_calculan_o_se_repiten(sesion, tabla, columna):
    assert columna not in columnas(sesion, tabla)


def test_ya_no_existen_las_tablas_clientes_ni_compatibilidades(sesion):
    tablas = set(inspect(sesion.get_bind()).get_table_names())

    assert "clientes" not in tablas
    assert "compatibilidades" not in tablas
    assert {
        "personas",
        "asesores",
        "tipos_moto",
        "categorias_accesorio",
        "fabricantes",
    } <= tablas


def test_las_contrasenas_de_usuarios_estan_hasheadas(sesion):
    cargar_todo(sesion)

    usuarios = sesion.scalars(select(UsuarioORM)).all()

    assert len(usuarios) == 8
    assert all(usuario.hash_contrasena.startswith("$2") for usuario in usuarios)


def test_los_parametros_que_cambio_el_administrador_no_se_pierden_al_recargar(sesion):
    cargar_todo(sesion)
    parametros = sesion.scalar(select(ParametrosCosto))
    parametros.precio_galon_cop = 18_000
    sesion.flush()

    cargar_todo(sesion)

    assert sesion.scalar(select(ParametrosCosto)).precio_galon_cop == 18_000


def test_sin_contrasenas_configuradas_no_se_crean_usuarios_ni_falla(sesion, monkeypatch):
    monkeypatch.delenv("CONTRASENA_ASESORES_DEMO", raising=False)
    monkeypatch.delenv("CONTRASENA_ADMIN_DEMO", raising=False)

    cargar_todo(sesion)

    assert contar(sesion, UsuarioORM) == 0
    assert contar(sesion, Moto) == 60
