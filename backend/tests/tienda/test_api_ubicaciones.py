import unicodedata

import pytest

from app.infrastructure.memoria.datos_ubicaciones import DEPARTAMENTOS, MUNICIPIOS

TARIFAS_ESPERADAS = {
    "Bogotá D.C.": (9000, {1}),
    "Cundinamarca": (12000, {2}),
    **{
        nombre: (15000, {3})
        for nombre in (
            "Antioquia",
            "Boyacá",
            "Caldas",
            "Huila",
            "Meta",
            "Quindío",
            "Risaralda",
            "Santander",
            "Tolima",
            "Valle del Cauca",
        )
    },
    **{
        nombre: (29000, {6, 7, 8})
        for nombre in (
            "Amazonas",
            "Arauca",
            "Caquetá",
            "Chocó",
            "Guainía",
            "Guaviare",
            "Putumayo",
            "San Andrés y Providencia",
            "Vaupés",
            "Vichada",
        )
    },
    **{
        nombre: (19000, {4, 5})
        for nombre in (
            "Atlántico",
            "Bolívar",
            "Casanare",
            "Cauca",
            "Cesar",
            "Córdoba",
            "La Guajira",
            "Magdalena",
            "Nariño",
            "Norte de Santander",
            "Sucre",
        )
    },
}


def sin_tildes(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c)
    ).casefold()


def test_listar_departamentos_devuelve_los_33(cliente_http):
    respuesta = cliente_http.get("/departamentos")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 33
    assert len({departamento["codigo"] for departamento in cuerpo}) == 33
    assert set(cuerpo[0]) == {"codigo", "nombre", "costo_envio_cop", "dias_envio"}


def test_los_departamentos_salen_en_orden_alfabetico_por_nombre(cliente_http):
    nombres = [d["nombre"] for d in cliente_http.get("/departamentos").json()]
    assert nombres == sorted(nombres, key=sin_tildes)
    assert nombres[0] == "Amazonas"
    assert nombres.index("Córdoba") < nombres.index("Cundinamarca")


def test_bogota_tiene_la_tarifa_del_contrato(cliente_http):
    bogota = next(d for d in cliente_http.get("/departamentos").json() if d["codigo"] == "11")
    assert bogota == {
        "codigo": "11",
        "nombre": "Bogotá D.C.",
        "costo_envio_cop": 9000,
        "dias_envio": 1,
    }


def test_las_tarifas_de_todos_los_departamentos_respetan_las_reglas(cliente_http):
    cuerpo = cliente_http.get("/departamentos").json()
    assert {d["nombre"] for d in cuerpo} == set(TARIFAS_ESPERADAS)
    for departamento in cuerpo:
        costo, dias = TARIFAS_ESPERADAS[departamento["nombre"]]
        assert departamento["costo_envio_cop"] == costo
        assert departamento["dias_envio"] in dias


def test_listar_municipios_de_un_departamento(cliente_http):
    respuesta = cliente_http.get("/departamentos/05/municipios")
    assert respuesta.status_code == 200
    assert respuesta.json() == [
        {"codigo": "05088", "nombre": "Bello"},
        {"codigo": "05266", "nombre": "Envigado"},
        {"codigo": "05001", "nombre": "Medellín"},
    ]


def test_listar_municipios_de_bogota(cliente_http):
    respuesta = cliente_http.get("/departamentos/11/municipios")
    assert respuesta.json() == [{"codigo": "11001", "nombre": "Bogotá D.C."}]


def test_cada_departamento_tiene_municipios_con_su_prefijo(cliente_http):
    for codigo, _, _, _ in DEPARTAMENTOS:
        respuesta = cliente_http.get(f"/departamentos/{codigo}/municipios")
        assert respuesta.status_code == 200
        municipios = respuesta.json()
        assert municipios
        assert all(m["codigo"].startswith(codigo) and len(m["codigo"]) == 5 for m in municipios)


def test_los_datos_semilla_tienen_entre_uno_y_tres_municipios_por_departamento():
    assert len(MUNICIPIOS) == 33
    assert all(1 <= len(municipios) <= 3 for municipios in MUNICIPIOS.values())
    assert [codigo for codigo, m in MUNICIPIOS.items() if len(m) < 2] == ["11"]


@pytest.mark.parametrize("codigo", ["00", "99999", "abc"])
def test_municipios_de_departamento_inexistente_responde_404(cliente_http, codigo):
    respuesta = cliente_http.get(f"/departamentos/{codigo}/municipios")
    assert respuesta.status_code == 404
    assert codigo in respuesta.json()["detail"]


def test_consultar_tarifa_de_envio(cliente_http):
    respuesta = cliente_http.get("/envios/tarifa", params={"departamento": "11"})
    assert respuesta.status_code == 200
    assert respuesta.json() == {"departamento": "11", "costo_envio_cop": 9000, "dias_envio": 1}


def test_la_tarifa_coincide_con_la_del_listado(cliente_http):
    for departamento in cliente_http.get("/departamentos").json():
        tarifa = cliente_http.get("/envios/tarifa", params={"departamento": departamento["codigo"]})
        assert tarifa.json() == {
            "departamento": departamento["codigo"],
            "costo_envio_cop": departamento["costo_envio_cop"],
            "dias_envio": departamento["dias_envio"],
        }


def test_tarifa_de_departamento_inexistente_responde_404(cliente_http):
    assert cliente_http.get("/envios/tarifa", params={"departamento": "00"}).status_code == 404


def test_tarifa_sin_departamento_responde_422(cliente_http):
    assert cliente_http.get("/envios/tarifa").status_code == 422
