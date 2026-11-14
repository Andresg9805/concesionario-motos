from app.domain.atencion import Rol, Usuario
from app.domain.catalogo import Marca, Moto, TipoMoto
from app.domain.costo_real import ParametrosCosto, TarifaSoat

ANIO_CATALOGO = 2026


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


CATALOGO: tuple[tuple[int, str, int, TipoMoto, int, int, float, int], ...] = (
    (1, "CB125F", 124, TipoMoto.NAKED, 7_990_000, 6, 140.0, 45),
    (1, "XR150L", 149, TipoMoto.TRAIL, 10_490_000, 5, 115.0, 55),
    (1, "CB190R", 184, TipoMoto.NAKED, 12_890_000, 4, 105.0, 55),
    (1, "XR190L", 184, TipoMoto.TRAIL, 13_490_000, 3, 100.0, 60),
    (1, "CB300F Twister", 293, TipoMoto.NAKED, 17_990_000, 4, 90.0, 70),
    (1, "XRE 300 Rally", 286, TipoMoto.DOBLE_PROPOSITO, 24_490_000, 3, 85.0, 75),
    (1, "CBR500R", 471, TipoMoto.DEPORTIVA, 41_990_000, 2, 70.0, 95),
    (1, "CRF1100L Africa Twin", 1084, TipoMoto.DOBLE_PROPOSITO, 89_990_000, 1, 50.0, 140),
    (2, "KLX 110R", 112, TipoMoto.TRAIL, 13_490_000, 2, 130.0, 50),
    (2, "W175", 177, TipoMoto.NAKED, 11_990_000, 4, 110.0, 55),
    (2, "KLX 150", 144, TipoMoto.TRAIL, 14_290_000, 3, 115.0, 55),
    (2, "Versys-X 300", 296, TipoMoto.DOBLE_PROPOSITO, 28_990_000, 2, 80.0, 80),
    (2, "Z400", 399, TipoMoto.NAKED, 32_490_000, 3, 75.0, 85),
    (2, "Ninja 400", 399, TipoMoto.DEPORTIVA, 35_990_000, 2, 75.0, 90),
    (2, "Z900", 948, TipoMoto.NAKED, 64_990_000, 0, 50.0, 130),
    (3, "XTZ 125", 124, TipoMoto.TRAIL, 9_590_000, 5, 135.0, 45),
    (3, "FZ 15", 149, TipoMoto.NAKED, 10_990_000, 6, 120.0, 50),
    (3, "XTZ 150", 149, TipoMoto.TRAIL, 11_490_000, 4, 115.0, 55),
    (3, "FZ 25", 249, TipoMoto.NAKED, 15_490_000, 3, 95.0, 65),
    (3, "YZF-R15 V4", 155, TipoMoto.DEPORTIVA, 17_490_000, 2, 105.0, 60),
    (3, "XTZ 250", 249, TipoMoto.DOBLE_PROPOSITO, 21_490_000, 3, 90.0, 70),
    (3, "MT-03", 321, TipoMoto.NAKED, 29_990_000, 2, 80.0, 80),
)


def motos_iniciales() -> list[Moto]:
    marcas = {marca.id: marca for marca in marcas_iniciales()}
    return [
        Moto(
            id=indice,
            marca=marcas[marca_id],
            modelo=modelo,
            anio=ANIO_CATALOGO,
            cilindraje_cc=cilindraje,
            tipo=tipo,
            precio_cop=precio,
            stock=stock,
            consumo_km_galon=consumo,
            costo_mantenimiento_km_cop=mantenimiento,
            descripcion=f"{marcas[marca_id].nombre} {modelo} de {cilindraje} cc.",
        )
        for indice, (
            marca_id,
            modelo,
            cilindraje,
            tipo,
            precio,
            stock,
            consumo,
            mantenimiento,
        ) in enumerate(CATALOGO, start=1)
    ]


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
