from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.accesorio import Accesorio

DESC_HON_MAN_001 = (
    "Lubricante de cadena oficial Pro Honda de alto rendimiento "
    "para transmisiones por cadena."
)
DESC_HON_MAN_002 = (
    "Lubricante Pro Honda Moto 4T 10W-30 Semisintético formulado "
    "para proteger el motor y optimizar los cambios."
)
DESC_HON_MAN_003 = (
    "Lubricante Pro Honda Moto 4T 10W-30 Full Sintético de máxima "
    "protección y rendimiento térmico superior."
)
DESC_HON_MAN_004 = (
    "Renovador de partes plásticas Pro Honda que devuelve el brillo "
    "original y protege contra rayos UV."
)
DESC_HON_MAN_005 = (
    "Casco-fresh desinfectante y aromatizante para cascos Pro Honda, "
    "elimina malos olores y bacterias."
)
DESC_SHO_CHA_001 = (
    "SHOEI Chaqueta Softshell 2.0 ligera, cortavientos e impermeable "
    "para uso urbano y rutero."
)
DESC_KAW_CHA_002 = (
    "Kawasaki Chaquetilla con cremallera Sports 2026 de diseño deportivo "
    "y ajuste ergonómico oficial."
)
DESC_KAW_CHA_003 = (
    "Kawasaki Chaqueta softshell WSBK 2026 inspirada en el mundial "
    "de Superbikes con máxima protección térmica."
)
DESC_HON_CHA_004 = (
    "Honda CHAQUETA COACH ELSINORE de estilo clásico retro con gran "
    "comodidad y acabados de alta calidad."
)
DESC_YAM_CHA_005 = (
    "Yamaha CORTAVIENTOS YAMAHA MULTI GRIS AZUL liviano y versátil "
    "para protección contra el clima."
)
DESC_SHO_CAS_001 = (
    "SHOEI X-Fifteen casco integral de altas prestaciones aerodinámicas "
    "para uso en circuito y alta velocidad."
)
DESC_SHO_CAS_002 = (
    "SHOEI RF-SR2 casco deportivo de calle con excelente ventilación, "
    "comodidad y certificación de seguridad avanzada."
)
DESC_SHO_CAS_003 = (
    "SHOEI RF-1500 LINE UP casco integral equilibrado con diseño gráfico "
    "moderno y gran ligereza."
)
DESC_SHO_CAS_004 = (
    "SHOEI Neotec 3 Fragments casco modular de turismo con visor solar "
    "integrado y alta insonorización."
)
DESC_SHO_CAS_005 = (
    "SHOEI Hornet X2 casco dual-sport/adventure versátil para uso en "
    "asfalto y off-road con visera optimizada."
)
DESC_ALP_GUA_001 = (
    "Alpinestars Techdura guantes off-road duraderos con refuerzos "
    "en nudillos y excelente agarre."
)
DESC_ALP_GUA_002 = (
    "Alpinestars Pro-Dura 2026 guantes deportivos de alta protección "
    "con certificación y máxima ventilación."
)
DESC_ALP_GUA_003 = (
    "Alpinestars Full Bore V2 Gloves ligeros y transpirables para "
    "conducción off-road y aventura."
)
DESC_ALP_GUA_004 = (
    "Alpinestars Megawatt V2 Gloves reforzados y diseñados para "
    "rendimiento superior en enduro y cross."
)
DESC_ALP_GUA_005 = (
    "Alpinestars Full Bore XT Gloves con protección adicional en los "
    "dedos y compatibilidad con pantallas táctiles."
)
DESC_SHO_MAL_001 = (
    "SHOEI Mochila 2.0 aerodinámica e impermeable diseñada para "
    "motociclistas con compartimentos seguros."
)
DESC_GIV_MAL_002 = (
    "GIVI Trekker Outback Evo Smart 42 maleta superior de aluminio de "
    "alta resistencia y gran capacidad."
)
DESC_GIV_MAL_003 = (
    "GIVI B37 Blade maleta trasera Monolock con capacidad ideal para "
    "un casco integral y uso diario en ciudad."
)
DESC_GIV_MAL_004 = (
    "GIVI Trekker Dolomiti DLM46 maleta lateral/superior de aluminio "
    "con diseño robusto y elegante estilo aventura."
)
DESC_GIV_MAL_005 = (
    "GIVI Trekker Alaska ALA44 maleta superior de aluminio con sistema "
    "de fijación MONOKEY para viajes largos."
)
DESC_ALP_ROD_001 = (
    "Protector De Rodilla Nucleon Morph STEALTH Alpinestars delgado, "
    "flexible y con certificación de impacto."
)
DESC_ALP_ROD_002 = (
    "Protectores De Rodillas Nucleon Flex Pro Alpinestars altamente "
    "ventilados con diseño ergonómico avanzado."
)
DESC_ALP_ROD_003 = (
    "Protectores De Rodillas Nucleon Flex Plus cómodos y ligeros para "
    "protección diaria en carretera."
)
DESC_ALP_ROD_004 = (
    "Alpinestars SX-1 Plasma Knee Protector con estructura rígida "
    "articulada y máxima cobertura off-road."
)
DESC_ALP_ROD_005 = (
    "Alpinestars Bionic Pro Plasma Knee Protectors de alto rendimiento "
    "para absorción de impactos severos."
)
DESC_ALP_HOM_001 = (
    "Nucleon Flex Pro Shoulder Protectors de Alpinestars con estructura "
    "celular flexible y segura."
)
DESC_ALP_HOM_002 = (
    "Alpinestars Nucleon Flex Plus Shoulder Protectors ligeros y "
    "adaptables para chaquetas deportivas."
)
DESC_SAS_HOM_003 = (
    "SAS-TEC SC-1/02 protector viscoelástico de hombro con memoria "
    "de forma y alta absorción de energía."
)
DESC_SAS_HOM_004 = (
    "SAS-TEC SC-1/01 protector ergonómico y delgado para inserción "
    "en chaquetas de moto."
)
DESC_SAS_HOM_005 = (
    "SAS-TEC SC-1/03 protector de hombro de alto nivel de protección "
    "para uso touring y deportivo."
)

ACCESORIOS_INICIALES = [

    {
        "sku": "HON-MAN-001",
        "nombre": "Lubricante de cadena Pro Honda",
        "categoria": "MANTENIMIENTO",
        "descripcion": DESC_HON_MAN_001,
        "precio_cop": 45000,
        "stock": 15,
        "imagen_url": "foto",
    },
    {
        "sku": "HON-MAN-002",
        "nombre": "Litro Lubricante Pro Honda Moto 4T 10W-30 Semisintético",
        "categoria": "MANTENIMIENTO",
        "descripcion": DESC_HON_MAN_002,
        "precio_cop": 38000,
        "stock": 20,
        "imagen_url": "foto",
    },
    {
        "sku": "HON-MAN-003",
        "nombre": "Litro Lubricante Pro Honda Moto 4T 10W-30 Full Sintético",
        "categoria": "MANTENIMIENTO",
        "descripcion": DESC_HON_MAN_003,
        "precio_cop": 62000,
        "stock": 12,
        "imagen_url": "foto",
    },
    {
        "sku": "HON-MAN-004",
        "nombre": "Renovador de partes plásticas Pro Honda",
        "categoria": "MANTENIMIENTO",
        "descripcion": DESC_HON_MAN_004,
        "precio_cop": 32000,
        "stock": 18,
        "imagen_url": "foto",
    },
    {
        "sku": "HON-MAN-005",
        "nombre": "Casco-fresh desinfectante cascos Pro Honda",
        "categoria": "MANTENIMIENTO",
        "descripcion": DESC_HON_MAN_005,
        "precio_cop": 28000,
        "stock": 25,
        "imagen_url": "foto",
    },

    {
        "sku": "SHO-CHA-001",
        "nombre": "SHOEI Chaqueta Softshell 2.0",
        "categoria": "CHAQUETA",
        "descripcion": DESC_SHO_CHA_001,
        "precio_cop": 480000,
        "stock": 5,
        "imagen_url": "foto",
    },
    {
        "sku": "KAW-CHA-002",
        "nombre": "Kawasaki Chaquetilla con cremallera Sports 2026",
        "categoria": "CHAQUETA",
        "descripcion": DESC_KAW_CHA_002,
        "precio_cop": 520000,
        "stock": 4,
        "imagen_url": "foto",
    },
    {
        "sku": "KAW-CHA-003",
        "nombre": "Kawasaki Chaqueta softshell WSBK 2026",
        "categoria": "CHAQUETA",
        "descripcion": DESC_KAW_CHA_003,
        "precio_cop": 650000,
        "stock": 3,
        "imagen_url": "foto",
    },
    {
        "sku": "HON-CHA-004",
        "nombre": "Honda CHAQUETA COACH ELSINORE",
        "categoria": "CHAQUETA",
        "descripcion": DESC_HON_CHA_004,
        "precio_cop": 450000,
        "stock": 6,
        "imagen_url": "foto",
    },
    {
        "sku": "YAM-CHA-005",
        "nombre": "Yamaha CORTAVIENTOS YAMAHA MULTI GRIS AZUL",
        "categoria": "CHAQUETA",
        "descripcion": DESC_YAM_CHA_005,
        "precio_cop": 310000,
        "stock": 8,
        "imagen_url": "foto",
    },

    {
        "sku": "SHO-CAS-001",
        "nombre": "SHOEI X-Fifteen",
        "categoria": "CASCO",
        "descripcion": DESC_SHO_CAS_001,
        "precio_cop": 3500000,
        "stock": 3,
        "imagen_url": "foto",
    },
    {
        "sku": "SHO-CAS-002",
        "nombre": "SHOEI RF-SR2",
        "categoria": "CASCO",
        "descripcion": DESC_SHO_CAS_002,
        "precio_cop": 2200000,
        "stock": 4,
        "imagen_url": "foto",
    },
    {
        "sku": "SHO-CAS-003",
        "nombre": "SHOEI RF-1500 LINE UP",
        "categoria": "CASCO",
        "descripcion": DESC_SHO_CAS_003,
        "precio_cop": 2400000,
        "stock": 4,
        "imagen_url": "foto",
    },
    {
        "sku": "SHO-CAS-004",
        "nombre": "SHOEI Neotec 3 Fragments",
        "categoria": "CASCO",
        "descripcion": DESC_SHO_CAS_004,
        "precio_cop": 3100000,
        "stock": 2,
        "imagen_url": "foto",
    },
    {
        "sku": "SHO-CAS-005",
        "nombre": "SHOEI Hornet X2",
        "categoria": "CASCO",
        "descripcion": DESC_SHO_CAS_005,
        "precio_cop": 2800000,
        "stock": 3,
        "imagen_url": "foto",
    },

    {
        "sku": "ALP-GUA-001",
        "nombre": "alpinestars Guantes Techdura",
        "categoria": "GUANTES",
        "descripcion": DESC_ALP_GUA_001,
        "precio_cop": 290000,
        "stock": 7,
        "imagen_url": "foto",
    },
    {
        "sku": "ALP-GUA-002",
        "nombre": "alpinestars Guantes Pro-Dura 2026",
        "categoria": "GUANTES",
        "descripcion": DESC_ALP_GUA_002,
        "precio_cop": 340000,
        "stock": 6,
        "imagen_url": "foto",
    },
    {
        "sku": "ALP-GUA-003",
        "nombre": "Full Bore V2 Gloves",
        "categoria": "GUANTES",
        "descripcion": DESC_ALP_GUA_003,
        "precio_cop": 210000,
        "stock": 10,
        "imagen_url": "foto",
    },
    {
        "sku": "ALP-GUA-004",
        "nombre": "Megawatt V2 Gloves",
        "categoria": "GUANTES",
        "descripcion": DESC_ALP_GUA_004,
        "precio_cop": 260000,
        "stock": 8,
        "imagen_url": "foto",
    },
    {
        "sku": "ALP-GUA-005",
        "nombre": "Full Bore XT Gloves",
        "categoria": "GUANTES",
        "descripcion": DESC_ALP_GUA_005,
        "precio_cop": 240000,
        "stock": 9,
        "imagen_url": "foto",
    },
    {
        "sku": "SHO-MAL-001",
        "nombre": "SHOEI Mochila 2.0",
        "categoria": "MALETA",
        "descripcion": DESC_SHO_MAL_001,
        "precio_cop": 550000,
        "stock": 5,
        "imagen_url": "foto",
    },
    {
        "sku": "GIV-MAL-002",
        "nombre": "Trekker Outback Evo Smart 42",
        "categoria": "MALETA",
        "descripcion": DESC_GIV_MAL_002,
        "precio_cop": 2100000,
        "stock": 2,
        "imagen_url": "foto",
    },
    {
        "sku": "GIV-MAL-003",
        "nombre": "B37 Blade",
        "categoria": "MALETA",
        "descripcion": DESC_GIV_MAL_003,
        "precio_cop": 650000,
        "stock": 4,
        "imagen_url": "foto",
    },
    {
        "sku": "GIV-MAL-004",
        "nombre": "Trekker Dolomiti DLM46",
        "categoria": "MALETA",
        "descripcion": DESC_GIV_MAL_004,
        "precio_cop": 2300000,
        "stock": 2,
        "imagen_url": "foto",
    },
    {
        "sku": "GIV-MAL-005",
        "nombre": "Trekker Alaska ALA44",
        "categoria": "MALETA",
        "descripcion": DESC_GIV_MAL_005,
        "precio_cop": 2450000,
        "stock": 3,
        "imagen_url": "foto",
    },
    {
        "sku": "ALP-ROD-001",
        "nombre": "Protector De Rodilla Nucleon Morph STEALTH alpinestars",
        "categoria": "RODILLERA",
        "descripcion": DESC_ALP_ROD_001,
        "precio_cop": 450000,
        "stock": 5,
        "imagen_url": "foto",
    },
    {
        "sku": "ALP-ROD-002",
        "nombre": "Protectores De Rodillas Nucleon Flex Pro alpinestars",
        "categoria": "RODILLERA",
        "descripcion": DESC_ALP_ROD_002,
        "precio_cop": 380000,
        "stock": 6,
        "imagen_url": "foto",
    },
    {
        "sku": "ALP-ROD-003",
        "nombre": "Protectores De Rodillas Nucleon Flex Plus",
        "categoria": "RODILLERA",
        "descripcion": DESC_ALP_ROD_003,
        "precio_cop": 320000,
        "stock": 7,
        "imagen_url": "foto",
    },
    {
        "sku": "ALP-ROD-004",
        "nombre": "SX-1 Plasma Knee Protector",
        "categoria": "RODILLERA",
        "descripcion": DESC_ALP_ROD_004,
        "precio_cop": 490000,
        "stock": 4,
        "imagen_url": "foto",
    },
    {
        "sku": "ALP-ROD-005",
        "nombre": "Bionic Pro Plasma Knee Protectors",
        "categoria": "RODILLERA",
        "descripcion": DESC_ALP_ROD_005,
        "precio_cop": 580000,
        "stock": 3,
        "imagen_url": "foto",
    },


    {
        "sku": "ALP-HOM-001",
        "nombre": "Protectores De Hombros Nucleon Flex Pro alpinestars",
        "categoria": "HOMBRERA",
        "descripcion": DESC_ALP_HOM_001,
        "precio_cop": 210000,
        "stock": 8,
        "imagen_url": "foto",
    },
    {
        "sku": "ALP-HOM-002",
        "nombre": "Nucleon Flex Plus Shoulder Protectors",
        "categoria": "HOMBRERA",
        "descripcion": DESC_ALP_HOM_002,
        "precio_cop": 190000,
        "stock": 8,
        "imagen_url": "foto",
    },
    {
        "sku": "SAS-HOM-003",
        "nombre": "SC-1/02",
        "categoria": "HOMBRERA",
        "descripcion": DESC_SAS_HOM_003,
        "precio_cop": 150000,
        "stock": 10,
        "imagen_url": "foto",
    },
    {
        "sku": "SAS-HOM-004",
        "nombre": "SC-1/01",
        "categoria": "HOMBRERA",
        "descripcion": DESC_SAS_HOM_004,
        "precio_cop": 130000,
        "stock": 10,
        "imagen_url": "foto",
    },
    {
        "sku": "SAS-HOM-005",
        "nombre": "SC-1/03",
        "categoria": "HOMBRERA",
        "descripcion": DESC_SAS_HOM_005,
        "precio_cop": 170000,
        "stock": 9,
        "imagen_url": "foto",
    },
]


def seed_accesorios(db: Session) -> None:
    for datos in ACCESORIOS_INICIALES:
        accesorio_existente = db.scalar(
            select(Accesorio).where(
                Accesorio.sku == datos["sku"]
            )
        )

        if accesorio_existente is None:
            db.add(Accesorio(**datos))
