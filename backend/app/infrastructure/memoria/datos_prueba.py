from typing import Any

from app.domain.atencion import Rol, Usuario
from app.domain.catalogo import CategoriaLicencia, Marca, Moto, TipoMoto
from app.domain.costo_real import ParametrosCosto, TarifaSoat
from app.domain.tienda import Accesorio, CategoriaAccesorio
from app.infrastructure.db.seeds.accesorios import ACCESORIOS_INICIALES
from app.infrastructure.db.seeds.motos_honda import MOTOS_HONDA
from app.infrastructure.db.seeds.motos_kawasaki import MOTOS_KAWASAKI
from app.infrastructure.db.seeds.motos_yamaha import MOTOS_YAMAHA

MOTOS_POR_MARCA: tuple[tuple[int, list[dict[str, Any]]], ...] = (
    (1, MOTOS_HONDA),
    (2, MOTOS_KAWASAKI),
    (3, MOTOS_YAMAHA),
)


def marcas_iniciales() -> list[Marca]:
    return [
        Marca(
            id=1,
            nombre="Honda",
            color_hex="#CC0000",
            descripcion="Motos confiables para ciudad, trabajo y aventura.",
        ),
        Marca(
            id=2,
            nombre="Kawasaki",
            color_hex="#66CC33",
            descripcion="Desempeño deportivo y naked de carácter.",
        ),
        Marca(
            id=3,
            nombre="Yamaha",
            color_hex="#0033A0",
            descripcion="Tecnología y versatilidad del trail a la pista.",
        ),
    ]


def motos_iniciales() -> list[Moto]:
    marcas = {marca.id: marca for marca in marcas_iniciales()}
    motos: list[Moto] = []
    for marca_id, lista in MOTOS_POR_MARCA:
        for datos in lista:
            motos.append(
                Moto(
                    id=len(motos) + 1,
                    marca=marcas[marca_id],
                    modelo=datos["modelo"],
                    anio=datos["anio"],
                    cilindraje_cc=datos["cilindraje_cc"],
                    tipo=TipoMoto(datos["tipo"]),
                    categoria_licencia=CategoriaLicencia(datos["categoria_licencia"]),
                    precio_cop=datos["precio_cop"],
                    stock=datos["stock"],
                    consumo_km_galon=datos["consumo_km_galon"],
                    costo_mantenimiento_km_cop=datos["costo_mantenimiento_km_cop"],
                    descripcion=datos["descripcion"],
                    imagen_url=datos["imagen_url"],
                )
            )
    return motos


def parametros_iniciales() -> ParametrosCosto:
    return ParametrosCosto(
        id=1,
        precio_galon_cop=16_200,
        porcentaje_impuesto=1.5,
        tarifas_soat=[
            TarifaSoat(cilindraje_min=0, cilindraje_max=99, valor_anual_cop=256_000),
            TarifaSoat(cilindraje_min=100, cilindraje_max=200, valor_anual_cop=343_000),
            TarifaSoat(cilindraje_min=201, cilindraje_max=100_000, valor_anual_cop=790_000),
        ],
        valor_matricula_cop=520_000,
        valor_tramites_cop=380_000,
        tasa_mensual=0.0179,
    )


ASESORES: tuple[tuple[int, str, str, str], ...] = (
    (1, "Laura Ruiz", "laura.ruiz@candela.com", "3001112233"),
    (2, "Camilo Torres", "camilo.torres@candela.com", "3002223344"),
    (3, "Daniela Pardo", "daniela.pardo@candela.com", "3003334455"),
)


def asesores_iniciales(hash_contrasena: str) -> list[Usuario]:
    marcas = {marca.id: marca for marca in marcas_iniciales()}
    return [
        Usuario(
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            hash_contrasena=hash_contrasena,
            rol=Rol.ASESOR,
            marca_especialidad=marcas[marca_id],
        )
        for marca_id, nombre, correo, telefono in ASESORES
    ]


def accesorios_iniciales() -> list[Accesorio]:
    motos = motos_iniciales()
    return [
        Accesorio(
            id=indice,
            sku=datos["sku"],
            nombre=datos["nombre"],
            categoria=CategoriaAccesorio(datos["categoria"]),
            descripcion=datos["descripcion"],
            precio_cop=datos["precio_cop"],
            stock=datos["stock"],
            imagen_url=datos["imagen_url"],
            motos_compatibles=list(motos),
        )
        for indice, datos in enumerate(ACCESORIOS_INICIALES, start=1)
    ]
