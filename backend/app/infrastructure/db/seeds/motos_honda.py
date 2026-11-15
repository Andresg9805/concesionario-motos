from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.marca import Marca
from app.infrastructure.models.moto import Moto

DESC_CB500_HORNET = (
    "Naked bicilíndrica de media cilindrada, ideal para el día a día "
    "y con una estética agresiva heredada de la familia Hornet."
)

DESC_CB650R = (
    "Diseño Neo Sports Café con un motor tetracilíndrico en línea suave y potente, "
    "pensada para una conducción deportiva y refinada."
)

DESC_CB750_HORNET = (
    "Ligera y con excelente respuesta gracias a su motor bicilíndrico en paralelo "
    "de última generación, equilibrando agilidad y potencia pura."
)

DESC_CB1000F = (
    "Roadster de gran cilindrada de estilo clásico y contundente, diseñada para "
    "ofrecer un par motor imponente y presencia robusta en carretera."
)

DESC_CB1000_HORNET_SP = (
    "Versión de altas prestaciones de la familia naked, equipada con componentes "
    "de suspensión Öhlins, frenos Brembo y máxima potencia en circuito."
)

DESC_CBR500R = (
    "Deportiva de media cilindrada con estilo aerodinámico inspirado en MotoGP, "
    "ideal para una conducción deportiva accesible y polivalente."
)

DESC_CBR650R = (
    "Deportiva de media cilindrada con motor tetracilíndrico en línea, postura "
    "equilibrada y líneas agresivas que combinan rendimiento y confort diario."
)

DESC_CBR600RR = (
    "Supersport pura de altas revoluciones, desarrollada con tecnología de "
    "competición para ofrecer máxima precisión, agilidad en pista y aerodinámica avanzada."
)

DESC_CBR1000RR = (
    "Superbike de alto rendimiento que ofrece potencia descomunal, control "
    "electrónico refinado y una experiencia de pilotaje emocionante tanto en carretera "
    "como en circuito."
)

DESC_CBR1000RR_R_FIREBLADE_SP = (
    "La máxima expresión de velocidad de Honda, equipada con suspensión electrónica "
    "Öhlins de tercera generación, frenos Brembo Stylema y aerodinámica derivada de MotoGP."
)

DESC_CRF1100L_AFRICA_TWIN = (
    "Auténtica trail de aventura diseñada para dominar tanto el asfalto como los "
    "terrenos off-road más exigentes, con gran capacidad de respuesta y chasis equilibrado."
)

DESC_AFRICA_TWIN_ADVENTURE_SPORTS = (
    "Versión orientada al gran turismo de aventura, equipada con mayor autonomía, "
    "depósito de combustible ampliado y suspensiones electrónicas orientadas al confort rutero."
)

DESC_XL750_TRANSALP = (
    "Trail versátil y ligera de media cilindrada, heredera de una gran leyenda, "
    "perfecta para el uso diario y aventuras de fin de semana con excelente agilidad."
)

DESC_NC750X = (
    "Crossover práctica y eficiente para el día a día, destacada por su bajo consumo, "
    "posición de manejo cómoda y un práctico compartimento de carga integrado."
)

DESC_NX500 = (
    "Crossover compacta y ligera, ideal para licencias A2, que combina un estilo "
    "aventurero moderno con un manejo accesible y ágil en cualquier ruta."
)

DESC_CRF450RL = (
    "Auténtica moto de enduro de competición adaptada para la calle, con un rendimiento "
    "off-road extremo, ligereza inigualable y chasis de aluminio de alta resistencia."
)

DESC_CRF300L = (
    "Ligera, divertida y sumamente versátil, diseñada para sortear el tráfico urbano "
    "con facilidad y ofrecer excelentes prestaciones en caminos destapados."
)

DESC_XR650L = (
    "Legendaria doble propósito de gran cilindrada con motor monocilíndrico enfriado "
    "por aire, robusta, duradera y lista para cualquier desafío todoterreno."
)

DESC_XR150L = (
    "Trabajadora incansable, económica y resistente, ideal para el trabajo diario en "
    "zonas rurales y urbanas gracias a su gran durabilidad y facilidad de manejo."
)

DESC_XR190L = (
    "Evolución con inyección electrónica PGM-FI, que combina la robustez y polivalencia "
    "de la familia XR con un mejor desempeño y eficiencia para el día a día."
)


MOTOS_HONDA: list[dict[str, Any]] = [
    {
        "modelo": "CB500 HORNET",
        "anio": 2027,
        "cilindraje_cc": 471,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 32990000,
        "stock": 5,
        "consumo_km_galon": 85.0,
        "costo_mantenimiento_km_cop": 55,
        "descripcion": DESC_CB500_HORNET,
        "imagen_url": "",
    },
    {
        "modelo": "CB650R",
        "anio": 2027,
        "cilindraje_cc": 649,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 58990000,
        "stock": 3,
        "consumo_km_galon": 58.0,
        "costo_mantenimiento_km_cop": 120,
        "descripcion": DESC_CB650R,
        "imagen_url": "",
    },
    {
        "modelo": "CB750 HORNET",
        "anio": 2027,
        "cilindraje_cc": 755,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 48990000,
        "stock": 4,
        "consumo_km_galon": 65.0,
        "costo_mantenimiento_km_cop": 95,
        "descripcion": DESC_CB750_HORNET,
        "imagen_url": "",
    },
    {
        "modelo": "CB1000F",
        "anio": 2027,
        "cilindraje_cc": 998,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 65990000,
        "stock": 2,
        "consumo_km_galon": 45.0,
        "costo_mantenimiento_km_cop": 180,
        "descripcion": DESC_CB1000F,
        "imagen_url": "",
    },
    {
        "modelo": "CB1000 HORNET SP",
        "anio": 2027,
        "cilindraje_cc": 999,
        "tipo": "NAKED",
        "categoria_licencia": "A2",
        "precio_cop": 78990000,
        "stock": 1,
        "consumo_km_galon": 40.0,
        "costo_mantenimiento_km_cop": 210,
        "descripcion": DESC_CB1000_HORNET_SP,
        "imagen_url": "",
    },
    {
        "modelo": "CBR500R",
        "anio": 2027,
        "cilindraje_cc": 471,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 34990000,
        "stock": 4,
        "consumo_km_galon": 85.0,
        "costo_mantenimiento_km_cop": 60,
        "descripcion": DESC_CBR500R,
        "imagen_url": "",
    },
    {
        "modelo": "CBR650R",
        "anio": 2027,
        "cilindraje_cc": 649,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 61990000,
        "stock": 3,
        "consumo_km_galon": 58.0,
        "costo_mantenimiento_km_cop": 130,
        "descripcion": DESC_CBR650R,
        "imagen_url": "",
    },
    {
        "modelo": "CBR600RR",
        "anio": 2027,
        "cilindraje_cc": 599,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 74990000,
        "stock": 2,
        "consumo_km_galon": 48.0,
        "costo_mantenimiento_km_cop": 170,
        "descripcion": DESC_CBR600RR,
        "imagen_url": "",
    },
    {
        "modelo": "CBR1000RR",
        "anio": 2027,
        "cilindraje_cc": 998,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 95990000,
        "stock": 2,
        "consumo_km_galon": 40.0,
        "costo_mantenimiento_km_cop": 220,
        "descripcion": DESC_CBR1000RR,
        "imagen_url": "",
    },
    {
        "modelo": "CBR1000RR-R FIREBLADE SP",
        "anio": 2027,
        "cilindraje_cc": 1000,
        "tipo": "DEPORTIVA",
        "categoria_licencia": "A2",
        "precio_cop": 129990000,
        "stock": 1,
        "consumo_km_galon": 35.0,
        "costo_mantenimiento_km_cop": 280,
        "descripcion": DESC_CBR1000RR_R_FIREBLADE_SP,
        "imagen_url": "",
    },
    {
        "modelo": "CRF1100L AFRICA TWIN",
        "anio": 2027,
        "cilindraje_cc": 1084,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 79990000,
        "stock": 3,
        "consumo_km_galon": 52.0,
        "costo_mantenimiento_km_cop": 130,
        "descripcion": DESC_CRF1100L_AFRICA_TWIN,
        "imagen_url": "",
    },
    {
        "modelo": "AFRICA TWIN ADVENTURE SPORTS",
        "anio": 2027,
        "cilindraje_cc": 1084,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 89990000,
        "stock": 2,
        "consumo_km_galon": 50.0,
        "costo_mantenimiento_km_cop": 145,
        "descripcion": DESC_AFRICA_TWIN_ADVENTURE_SPORTS,
        "imagen_url": "",
    },
    {
        "modelo": "XL750 TRANSALP",
        "anio": 2027,
        "cilindraje_cc": 755,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 54990000,
        "stock": 4,
        "consumo_km_galon": 68.0,
        "costo_mantenimiento_km_cop": 95,
        "descripcion": DESC_XL750_TRANSALP,
        "imagen_url": "",
    },
    {
        "modelo": "NC750X",
        "anio": 2027,
        "cilindraje_cc": 745,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 48990000,
        "stock": 4,
        "consumo_km_galon": 82.0,
        "costo_mantenimiento_km_cop": 75,
        "descripcion": DESC_NC750X,
        "imagen_url": "",
    },
    {
        "modelo": "NX500",
        "anio": 2027,
        "cilindraje_cc": 471,
        "tipo": "TRAIL",
        "categoria_licencia": "A2",
        "precio_cop": 35990000,
        "stock": 5,
        "consumo_km_galon": 88.0,
        "costo_mantenimiento_km_cop": 60,
        "descripcion": DESC_NX500,
        "imagen_url": "",
    },
    {
        "modelo": "CRF450RL",
        "anio": 2027,
        "cilindraje_cc": 449,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 48990000,
        "stock": 2,
        "consumo_km_galon": 70.0,
        "costo_mantenimiento_km_cop": 95,
        "descripcion": DESC_CRF450RL,
        "imagen_url": "",
    },
    {
        "modelo": "CRF300L",
        "anio": 2027,
        "cilindraje_cc": 286,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 27990000,
        "stock": 4,
        "consumo_km_galon": 95.0,
        "costo_mantenimiento_km_cop": 50,
        "descripcion": DESC_CRF300L,
        "imagen_url": "",
    },
    {
        "modelo": "XR650L",
        "anio": 2027,
        "cilindraje_cc": 644,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 39990000,
        "stock": 3,
        "consumo_km_galon": 65.0,
        "costo_mantenimiento_km_cop": 75,
        "descripcion": DESC_XR650L,
        "imagen_url": "",
    },
    {
        "modelo": "XR150L",
        "anio": 2027,
        "cilindraje_cc": 149,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 9990000,
        "stock": 6,
        "consumo_km_galon": 125.0,
        "costo_mantenimiento_km_cop": 35,
        "descripcion": DESC_XR150L,
        "imagen_url": "",
    },
    {
        "modelo": "XR190L",
        "anio": 2027,
        "cilindraje_cc": 184,
        "tipo": "DOBLE_PROPOSITO",
        "categoria_licencia": "A2",
        "precio_cop": 12990000,
        "stock": 5,
        "consumo_km_galon": 110.0,
        "costo_mantenimiento_km_cop": 45,
        "descripcion": DESC_XR190L,
        "imagen_url": "",
    },
]


def seed_motos_honda(db: Session) -> None:
    marca = db.scalar(select(Marca).where(Marca.nombre.ilike("Honda")))
    if marca is None:
        return
    for datos in MOTOS_HONDA:
        moto_existente = db.scalar(
            select(Moto).where(
                Moto.marca_id == marca.id,
                Moto.modelo.ilike(datos["modelo"]),
            )
        )
        if moto_existente is None:
            db.add(Moto(**datos, marca_id=marca.id))
