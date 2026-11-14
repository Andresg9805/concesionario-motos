from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.moto import Moto

DESC_Z125 = (
    "La puerta de entrada perfecta al universo Supernaked de Kawasaki, "
    "con chasis ligero, suspensión trasera Uni Trak y diseño agresivo."
)

DESC_Z500 = (
    "Potente y manejable motor bicilíndrico en paralelo de 451 cc, "
    "con chasis ligero y maniobrable e intensidad visual de alto nivel."
)

DESC_Z900 = (
    "Supernaked completamente equipada con prestaciones y estilo Sugomi "
    "refinado, ofreciendo un equilibrio perfecto entre potencia y manejabilidad."
)

DESC_Z900_SE = (
    "Evolución de alta gama de la Z900 que incorpora componentes superiores, "
    "estilo Sugomi refinado y máximo equipamiento naked."
)

DESC_Z_H2_SE = (
    "En la cúspide absoluta, la única supernaked del mundo con motor "
    "Kawasaki Balanced Supercharged, KECS con Showa Skyhook y arsenal "
    "electrónico avanzado."
)

DESC_NINJA_H2R = (
    "Materialización extrema de ingeniería aeroespacial con motor supercharged "
    "de 998 cc, no homologada para vía pública y diseñada para máximo "
    "rendimiento en circuito."
)

DESC_NINJA_H2 = (
    "Ofrece la aceleración definitiva, estabilidad inigualable a alta "
    "velocidad, agilidad y un diseño icónico con motor sobrealimentado."
)

DESC_NINJA_H2_CARBON = (
    "Versión exclusiva que mantiene la aceleración definitiva y estabilidad "
    "con un diseño icónico que incorpora cúpula superior de fibra de carbono."
)

DESC_NINJA_H2_SX_SE = (
    "Turismo deportivo de alta gama con compresor, tecnología de vanguardia, "
    "prestaciones de confort insignia y el nivel más alto de equipamiento "
    "electrónico."
)

DESC_NINJA_1100_SX_SE = (
    "Diseñada para un mayor disfrute de conducción deportiva y rendimiento "
    "touring, incorporando suspensión electrónica y componentes de chasis "
    "estilo Supersport."
)

DESC_VERSYS_1100_SE = (
    "Equipamiento insignia de la gama Adventure Tourer, con motor de cuatro "
    "cilindros en línea optimizado para recorrer largas distancias con máximo "
    "confort, suspensión electrónica y conectividad avanzada."
)

DESC_VERSYS_900_SE = (
    "Modelo Adventure Tourer de carácter dinámico y deportivo, que incluye "
    "accesorios premium de serie, confort superior para viajar y tecnología "
    "avanzada con IMU."
)

DESC_VERSYS_650 = (
    "Paquete ágil y divertido para carreteras con curvas, ofreciendo mayor "
    "confort, practicidad touring y diseño emocional con un enfoque accesible."
)

DESC_KLE_650_SE = (
    "El puente perfecto entre el uso diario y la aventura, con capacidad rutera, "
    "confort de marcha superior y un llamativo diseño KLE inspirado en los rallies."
)

DESC_KLE_500_SE = (
    "Excelente opción para explorar fuera del asfalto gracias a su motor "
    "bicilíndrico de 451 cc, estilo rally, pantalla TFT a color, subchasis "
    "reforzado y gran capacidad touring."
)

DESC_KLX_300 = (
    "Doble propósito de alto rendimiento con suspensiones de largo recorrido, "
    "enfoque netamente off-road y homologada para rodar en ciudad y trocha."
)

DESC_KLX_230_S = (
    "Versátil doble propósito con altura de asiento accesible, excelente torque "
    "en bajos y gran agilidad para sortear tanto el tráfico urbano como caminos "
    "destapados."
)

DESC_KLX_150 = (
    "Motocicleta doble propósito ligera, diseñada para desplazamientos "
    "urbanos y recorridos por caminos destapados."
)

DESC_KLX_230_DF = (
    "Versión doble propósito con equipamiento orientado a la aventura y "
    "capacidad para desplazamientos urbanos y caminos destapados."
)

DESC_KLX_300_DF = (
    "Motocicleta doble propósito orientada a la aventura, con motor de 292 cc "
    "y capacidad para recorridos urbanos y todoterreno."
)

MOTOS_KAWASAKI = [
    {
        "marca_id": 3,
        "modelo": "Z125",
        "anio": 2027,
        "cilindraje_cc": 125,
        "tipo": "NAKED",
        "categoria_licencia": "A1",
        "precio_cop": 16990000,
        "stock": 5,
        "consumo_km_galon": 130.0,
        "costo_mantenimiento_km_cop": 45,
        "descripcion": DESC_Z125,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "Z500",
        "anio": 2027,
        "cilindraje_cc": 451,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 28990000,
        "stock": 4,
        "consumo_km_galon": 95.0,
        "costo_mantenimiento_km_cop": 65,
        "descripcion": DESC_Z500,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "Z900",
        "anio": 2027,
        "cilindraje_cc": 948,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 52990000,
        "stock": 3,
        "consumo_km_galon": 55.0,
        "costo_mantenimiento_km_cop": 110,
        "descripcion": DESC_Z900,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "Z900 SE",
        "anio": 2027,
        "cilindraje_cc": 948,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 61990000,
        "stock": 2,
        "consumo_km_galon": 54.0,
        "costo_mantenimiento_km_cop": 125,
        "descripcion": DESC_Z900_SE,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "Z H2 SE",
        "anio": 2027,
        "cilindraje_cc": 998,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 115000000,
        "stock": 1,
        "consumo_km_galon": 38.0,
        "costo_mantenimiento_km_cop": 220,
        "descripcion": DESC_Z_H2_SE,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "NINJA H2R",
        "anio": 2027,
        "cilindraje_cc": 998,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 245000000,
        "stock": 1,
        "consumo_km_galon": 30.0,
        "costo_mantenimiento_km_cop": 350,
        "descripcion": DESC_NINJA_H2R,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "NINJA H2",
        "anio": 2027,
        "cilindraje_cc": 998,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 155000000,
        "stock": 2,
        "consumo_km_galon": 35.0,
        "costo_mantenimiento_km_cop": 250,
        "descripcion": DESC_NINJA_H2,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "NINJA H2 CARBON",
        "anio": 2027,
        "cilindraje_cc": 998,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 168000000,
        "stock": 1,
        "consumo_km_galon": 35.0,
        "costo_mantenimiento_km_cop": 260,
        "descripcion": DESC_NINJA_H2_CARBON,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "NINJA H2 SX SE",
        "anio": 2027,
        "cilindraje_cc": 998,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 135000000,
        "stock": 2,
        "consumo_km_galon": 42.0,
        "costo_mantenimiento_km_cop": 210,
        "descripcion": DESC_NINJA_H2_SX_SE,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "NINJA 1100SX SE",
        "anio": 2027,
        "cilindraje_cc": 1099,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 74990000,
        "stock": 3,
        "consumo_km_galon": 50.0,
        "costo_mantenimiento_km_cop": 140,
        "descripcion": DESC_NINJA_1100_SX_SE,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "VERSYS 1100 SE",
        "anio": 2027,
        "cilindraje_cc": 1099,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 82990000,
        "stock": 2,
        "consumo_km_galon": 48.0,
        "costo_mantenimiento_km_cop": 140,
        "descripcion": DESC_VERSYS_1100_SE,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "VERSYS 900 SE",
        "anio": 2027,
        "cilindraje_cc": 900,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 64990000,
        "stock": 3,
        "consumo_km_galon": 55.0,
        "costo_mantenimiento_km_cop": 115,
        "descripcion": DESC_VERSYS_900_SE,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "VERSYS 650",
        "anio": 2027,
        "cilindraje_cc": 649,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 42990000,
        "stock": 4,
        "consumo_km_galon": 75.0,
        "costo_mantenimiento_km_cop": 80,
        "descripcion": DESC_VERSYS_650,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "KLE650 SE",
        "anio": 2027,
        "cilindraje_cc": 649,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 46990000,
        "stock": 3,
        "consumo_km_galon": 70.0,
        "costo_mantenimiento_km_cop": 85,
        "descripcion": DESC_KLE_650_SE,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "KLE500 SE",
        "anio": 2027,
        "cilindraje_cc": 451,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 35990000,
        "stock": 5,
        "consumo_km_galon": 92.0,
        "costo_mantenimiento_km_cop": 60,
        "descripcion": DESC_KLE_500_SE,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "KLX 300",
        "anio": 2027,
        "cilindraje_cc": 292,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 31990000,
        "stock": 3,
        "consumo_km_galon": 90.0,
        "costo_mantenimiento_km_cop": 60,
        "descripcion": DESC_KLX_300,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "KLX 230 S",
        "anio": 2027,
        "cilindraje_cc": 233,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 23990000,
        "stock": 5,
        "consumo_km_galon": 110.0,
        "costo_mantenimiento_km_cop": 45,
        "descripcion": DESC_KLX_230_S,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "KLX 150",
        "anio": 2027,
        "cilindraje_cc": 144,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A1",
        "precio_cop": 14990000,
        "stock": 4,
        "consumo_km_galon": 100.0,
        "costo_mantenimiento_km_cop": 40,
        "descripcion": DESC_KLX_150,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "KLX 230 DF",
        "anio": 2027,
        "cilindraje_cc": 233,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 28500000,
        "stock": 3,
        "consumo_km_galon": 100.0,
        "costo_mantenimiento_km_cop": 50,
        "descripcion": DESC_KLX_230_DF,
        "imagen_url": "foto",
    },
    {
        "marca_id": 3,
        "modelo": "KLX 300 DF",
        "anio": 2027,
        "cilindraje_cc": 292,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 40090000,
        "stock": 2,
        "consumo_km_galon": 90.0,
        "costo_mantenimiento_km_cop": 60,
        "descripcion": DESC_KLX_300_DF,
        "imagen_url": "foto",
    },
]


def seed_motos_kawasaki(db: Session) -> None:
    for datos in MOTOS_KAWASAKI:
        moto_existente = db.scalar(
            select(Moto).where(
                Moto.marca_id == datos["marca_id"],
                Moto.modelo.ilike(datos["modelo"]),
            )
        )

        if moto_existente is None:
            db.add(Moto(**datos))
