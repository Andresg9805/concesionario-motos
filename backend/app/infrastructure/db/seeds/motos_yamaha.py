from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.moto import Moto

DESC_FZ150 = (
    "Naked urbana con inyección electrónica Blue Core, diseño deportivo "
    "y eficiencia para el día a día."
)
DESC_FZ25 = (
    "Naked de cuarto de litro con ABS de doble canal, postura cómoda "
    "y buen torque en bajas revoluciones."
)
DESC_MT15 = (
    "Hypernaked compacta con VVA, chasis Deltabox y estética de la familia "
    "Master of Torque."
)
DESC_MT03 = (
    "Naked bicilíndrica ligera, de altas revoluciones y buen desempeño "
    "urbano y en carretera."
)
DESC_MT09 = (
    "Hypernaked de alto rendimiento con motor tricilíndrico CP3 y electrónica "
    "avanzada."
)
DESC_R15 = (
    "Superdeportiva ligera con VVA, control de tracción y diseño de la familia R."
)
DESC_R3 = (
    "Deportiva bicilíndrica equilibrada para carretera y pista, con postura "
    "aerodinámica y chasis ágil."
)
DESC_R7 = (
    "Supersport con motor CP2, perfil estilizado y gran torque en medios "
    "regímenes."
)
DESC_R9 = (
    "Deportiva de alto rendimiento con motor tricilíndrico CP3, electrónica "
    "avanzada y chasis Deltabox."
)
DESC_R1 = (
    "Superbike insignia con tecnología electrónica de competición y alto "
    "rendimiento en circuito."
)
DESC_TENERE = (
    "Viajera de aventura con motor CP2, chasis tubular ligero y componentes "
    "orientados al off-road."
)
DESC_SUPER_TENERE = (
    "Maxitrail de turismo de largo alcance con transmisión por cardán y "
    "suspensiones electrónicas."
)
DESC_WR250F = (
    "Motocicleta de enduro con motor de cuatro tiempos y componentes enfocados "
    "al desempeño fuera del asfalto."
)
DESC_WR450F = (
    "Motocicleta de enduro de alta cilindrada, diseñada para recorridos "
    "todoterreno exigentes."
)
DESC_XT250 = (
    "Doble propósito ligera y versátil, con motor de 249 cc y orientación para "
    "caminos pavimentados y destapados."
)
DESC_XTZ125 = (
    "Doble propósito ligera y accesible para uso urbano y caminos destapados, "
    "con buen rendimiento de combustible."
)
DESC_XTZ150 = (
    "Trail versátil con inyección electrónica, suspensión Monocross y comodidad "
    "para el día a día."
)
DESC_XTZ250 = (
    "Motocicleta robusta con ABS delantero, tablero digital y desempeño para "
    "distintos tipos de terreno."
)
DESC_WR125R = (
    "Doble propósito de baja cilindrada para desplazamientos cotidianos y "
    "caminos destapados."
)
DESC_WR250R = (
    "Doble propósito de altas prestaciones que combina agilidad off-road y "
    "durabilidad para trayectos largos."
)

MOTOS_YAMAHA = [

    {
        "marca_id": 1,
        "modelo": "FZ150 V3.0",
        "anio": 2027,
        "cilindraje_cc": 149,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 11800000,
        "stock": 5,
        "consumo_km_galon": 120.0,
        "costo_mantenimiento_km_cop": 40,
        "descripcion": DESC_FZ150,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "FZ25 ABS",
        "anio": 2027,
        "cilindraje_cc": 249,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 15300000,
        "stock": 4,
        "consumo_km_galon": 95.0,
        "costo_mantenimiento_km_cop": 55,
        "descripcion": DESC_FZ25,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "MT-15",
        "anio": 2027,
        "cilindraje_cc": 155,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 15500000,
        "stock": 4,
        "consumo_km_galon": 115.0,
        "costo_mantenimiento_km_cop": 45,
        "descripcion": DESC_MT15,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "MT-03",
        "anio": 2027,
        "cilindraje_cc": 321,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 31900000,
        "stock": 3,
        "consumo_km_galon": 80.0,
        "costo_mantenimiento_km_cop": 70,
        "descripcion": DESC_MT03,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "MT-09",
        "anio": 2027,
        "cilindraje_cc": 890,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 63000000,
        "stock": 2,
        "consumo_km_galon": 52.0,
        "costo_mantenimiento_km_cop": 120,
        "descripcion": DESC_MT09,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "R15 V4",
        "anio": 2027,
        "cilindraje_cc": 155,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 16100000,
        "stock": 4,
        "consumo_km_galon": 115.0,
        "costo_mantenimiento_km_cop": 45,
        "descripcion": DESC_R15,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "R3",
        "anio": 2027,
        "cilindraje_cc": 321,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 33900000,
        "stock": 3,
        "consumo_km_galon": 75.0,
        "costo_mantenimiento_km_cop": 75,
        "descripcion": DESC_R3,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "R7",
        "anio": 2027,
        "cilindraje_cc": 689,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 59000000,
        "stock": 2,
        "consumo_km_galon": 58.0,
        "costo_mantenimiento_km_cop": 125,
        "descripcion": DESC_R7,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "YZF-R9",
        "anio": 2027,
        "cilindraje_cc": 890,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 76000000,
        "stock": 2,
        "consumo_km_galon": 50.0,
        "costo_mantenimiento_km_cop": 160,
        "descripcion": DESC_R9,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "YZF-R1",
        "anio": 2027,
        "cilindraje_cc": 998,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 118000000,
        "stock": 1,
        "consumo_km_galon": 38.0,
        "costo_mantenimiento_km_cop": 250,
        "descripcion": DESC_R1,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "TÉNÉRÉ 700",
        "anio": 2027,
        "cilindraje_cc": 689,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 72000000,
        "stock": 2,
        "consumo_km_galon": 60.0,
        "costo_mantenimiento_km_cop": 110,
        "descripcion": DESC_TENERE,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "SUPER TÉNÉRÉ 1200 ZE",
        "anio": 2027,
        "cilindraje_cc": 1199,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 98000000,
        "stock": 1,
        "consumo_km_galon": 45.0,
        "costo_mantenimiento_km_cop": 180,
        "descripcion": DESC_SUPER_TENERE,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "WR250F",
        "anio": 2027,
        "cilindraje_cc": 250,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 52000000,
        "stock": 2,
        "consumo_km_galon": 55.0,
        "costo_mantenimiento_km_cop": 130,
        "descripcion": DESC_WR250F,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "WR450F",
        "anio": 2027,
        "cilindraje_cc": 450,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 58000000,
        "stock": 1,
        "consumo_km_galon": 48.0,
        "costo_mantenimiento_km_cop": 160,
        "descripcion": DESC_WR450F,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "XT250",
        "anio": 2027,
        "cilindraje_cc": 249,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 28500000,
        "stock": 3,
        "consumo_km_galon": 90.0,
        "costo_mantenimiento_km_cop": 65,
        "descripcion": DESC_XT250,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "XTZ 125",
        "anio": 2027,
        "cilindraje_cc": 124,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A1",
        "precio_cop": 10600000,
        "stock": 5,
        "consumo_km_galon": 125.0,
        "costo_mantenimiento_km_cop": 35,
        "descripcion": DESC_XTZ125,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "XTZ 150",
        "anio": 2027,
        "cilindraje_cc": 149,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 12500000,
        "stock": 4,
        "consumo_km_galon": 115.0,
        "costo_mantenimiento_km_cop": 42,
        "descripcion": DESC_XTZ150,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "XTZ 250",
        "anio": 2027,
        "cilindraje_cc": 249,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 26500000,
        "stock": 3,
        "consumo_km_galon": 90.0,
        "costo_mantenimiento_km_cop": 60,
        "descripcion": DESC_XTZ250,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "WR125R",
        "anio": 2027,
        "cilindraje_cc": 125,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A1",
        "precio_cop": 21500000,
        "stock": 3,
        "consumo_km_galon": 120.0,
        "costo_mantenimiento_km_cop": 45,
        "descripcion": DESC_WR125R,
        "imagen_url": "foto",
    },
    {
        "marca_id": 1,
        "modelo": "WR250R",
        "anio": 2027,
        "cilindraje_cc": 250,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 38900000,
        "stock": 3,
        "consumo_km_galon": 85.0,
        "costo_mantenimiento_km_cop": 70,
        "descripcion": DESC_WR250R,
        "imagen_url": "foto",
    },
]


def seed_motos_yamaha(db: Session) -> None:
    for datos in MOTOS_YAMAHA:
        moto_existente = db.scalar(
            select(Moto).where(
                Moto.marca_id == datos["marca_id"],
                Moto.modelo.ilike(datos["modelo"]),
            )
        )

        if moto_existente is None:
            db.add(Moto(**datos))
