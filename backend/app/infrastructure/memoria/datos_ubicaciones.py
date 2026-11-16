from app.domain.tienda import Departamento, Municipio

TARIFA_BOGOTA = (9_000, 1)
TARIFA_CUNDINAMARCA = (12_000, 2)
TARIFA_CENTRAL = (15_000, 3)
TARIFA_INTERMEDIA = (19_000, 4)
TARIFA_REMOTA = (29_000, 6)

DEPARTAMENTOS: tuple[tuple[str, str, int, int], ...] = (
    ("91", "Amazonas", 29_000, 7),
    ("05", "Antioquia", *TARIFA_CENTRAL),
    ("81", "Arauca", *TARIFA_REMOTA),
    ("08", "Atlántico", *TARIFA_INTERMEDIA),
    ("11", "Bogotá D.C.", *TARIFA_BOGOTA),
    ("13", "Bolívar", *TARIFA_INTERMEDIA),
    ("15", "Boyacá", *TARIFA_CENTRAL),
    ("17", "Caldas", *TARIFA_CENTRAL),
    ("18", "Caquetá", *TARIFA_REMOTA),
    ("85", "Casanare", *TARIFA_INTERMEDIA),
    ("19", "Cauca", *TARIFA_INTERMEDIA),
    ("20", "Cesar", *TARIFA_INTERMEDIA),
    ("27", "Chocó", 29_000, 7),
    ("23", "Córdoba", *TARIFA_INTERMEDIA),
    ("25", "Cundinamarca", *TARIFA_CUNDINAMARCA),
    ("94", "Guainía", 29_000, 8),
    ("95", "Guaviare", 29_000, 7),
    ("41", "Huila", *TARIFA_CENTRAL),
    ("44", "La Guajira", 19_000, 5),
    ("47", "Magdalena", *TARIFA_INTERMEDIA),
    ("50", "Meta", *TARIFA_CENTRAL),
    ("52", "Nariño", 19_000, 5),
    ("54", "Norte de Santander", *TARIFA_INTERMEDIA),
    ("86", "Putumayo", *TARIFA_REMOTA),
    ("63", "Quindío", *TARIFA_CENTRAL),
    ("66", "Risaralda", *TARIFA_CENTRAL),
    ("88", "San Andrés y Providencia", 29_000, 8),
    ("68", "Santander", *TARIFA_CENTRAL),
    ("70", "Sucre", *TARIFA_INTERMEDIA),
    ("73", "Tolima", *TARIFA_CENTRAL),
    ("76", "Valle del Cauca", *TARIFA_CENTRAL),
    ("97", "Vaupés", 29_000, 8),
    ("99", "Vichada", 29_000, 8),
)

MUNICIPIOS: dict[str, tuple[tuple[str, str], ...]] = {
    "05": (("05001", "Medellín"), ("05088", "Bello"), ("05266", "Envigado")),
    "08": (("08001", "Barranquilla"), ("08433", "Malambo"), ("08758", "Soledad")),
    "11": (("11001", "Bogotá D.C."),),
    "13": (
        ("13001", "Cartagena de Indias"),
        ("13244", "El Carmen de Bolívar"),
        ("13430", "Magangué"),
    ),
    "15": (("15001", "Tunja"), ("15238", "Duitama"), ("15759", "Sogamoso")),
    "17": (("17001", "Manizales"), ("17174", "Chinchiná"), ("17380", "La Dorada")),
    "18": (
        ("18001", "Florencia"),
        ("18150", "Cartagena del Chairá"),
        ("18753", "San Vicente del Caguán"),
    ),
    "19": (("19001", "Popayán"), ("19573", "Puerto Tejada"), ("19698", "Santander de Quilichao")),
    "20": (("20001", "Valledupar"), ("20011", "Aguachica"), ("20013", "Agustín Codazzi")),
    "23": (("23001", "Montería"), ("23417", "Lorica"), ("23660", "Sahagún")),
    "25": (("25175", "Chía"), ("25754", "Soacha"), ("25899", "Zipaquirá")),
    "27": (("27001", "Quibdó"), ("27361", "Istmina"), ("27615", "Riosucio")),
    "41": (("41001", "Neiva"), ("41298", "Garzón"), ("41551", "Pitalito")),
    "44": (("44001", "Riohacha"), ("44430", "Maicao"), ("44847", "Uribia")),
    "47": (("47001", "Santa Marta"), ("47189", "Ciénaga"), ("47288", "Fundación")),
    "50": (("50001", "Villavicencio"), ("50006", "Acacías"), ("50313", "Granada")),
    "52": (("52001", "Pasto"), ("52356", "Ipiales"), ("52835", "San Andrés de Tumaco")),
    "54": (("54001", "Cúcuta"), ("54498", "Ocaña"), ("54518", "Pamplona")),
    "63": (("63001", "Armenia"), ("63130", "Calarcá"), ("63401", "La Tebaida")),
    "66": (("66001", "Pereira"), ("66170", "Dosquebradas"), ("66682", "Santa Rosa de Cabal")),
    "68": (("68001", "Bucaramanga"),("68276", "Floridablanca"),("68307", "Girón"),("68861", "Vélez")
           ),
    "70": (("70001", "Sincelejo"), ("70215", "Corozal"), ("70708", "San Marcos")),
    "73": (("73001", "Ibagué"), ("73268", "Espinal"), ("73449", "Melgar")),
    "76": (("76001", "Cali"), ("76109", "Buenaventura"), ("76520", "Palmira")),
    "81": (("81001", "Arauca"), ("81736", "Saravena"), ("81794", "Tame")),
    "85": (("85001", "Yopal"), ("85010", "Aguazul"), ("85410", "Tauramena")),
    "86": (("86001", "Mocoa"), ("86568", "Puerto Asís"), ("86865", "Valle del Guamuez")),
    "88": (("88001", "San Andrés"), ("88564", "Providencia")),
    "91": (("91001", "Leticia"), ("91540", "Puerto Nariño")),
    "94": (("94001", "Inírida"), ("94343", "Barranco Minas")),
    "95": (("95001", "San José del Guaviare"), ("95015", "Calamar"), ("95025", "El Retorno")),
    "97": (("97001", "Mitú"), ("97161", "Carurú"), ("97666", "Taraira")),
    "99": (("99001", "Puerto Carreño"), ("99524", "La Primavera"), ("99624", "Santa Rosalía")),
}


def departamentos_iniciales() -> list[Departamento]:
    return [
        Departamento(codigo=codigo, nombre=nombre, costo_envio_cop=costo, dias_envio=dias)
        for codigo, nombre, costo, dias in DEPARTAMENTOS
    ]


def municipios_iniciales() -> list[Municipio]:
    departamentos = {
        departamento.codigo: departamento for departamento in departamentos_iniciales()
    }
    return [
        Municipio(codigo=codigo, nombre=nombre, departamento=departamentos[departamento_codigo])
        for departamento_codigo, municipios in MUNICIPIOS.items()
        for codigo, nombre in municipios
    ]
