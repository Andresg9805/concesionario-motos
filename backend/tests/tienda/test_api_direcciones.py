import pytest

from tests.tienda.conftest import DIRECCION

ANA = "ana@correo.com"
LUIS = "luis@correo.com"
ASESORA = "laura.ruiz@candela.com"


def crear(cliente_http, headers, **cambios):
    return cliente_http.post("/mis-direcciones", json={**DIRECCION, **cambios}, headers=headers)


def test_crear_direccion_responde_201_con_id_y_los_mismos_campos(cliente_http, token_de):
    respuesta = crear(cliente_http, token_de(ANA))
    assert respuesta.status_code == 201
    assert respuesta.json() == {"id": 1, **DIRECCION}


def test_crear_direccion_sin_detalle(cliente_http, token_de):
    cuerpo = {k: v for k, v in DIRECCION.items() if k != "detalle"}
    respuesta = cliente_http.post("/mis-direcciones", json=cuerpo, headers=token_de(ANA))
    assert respuesta.status_code == 201
    assert respuesta.json()["direccion"] == DIRECCION["direccion"]
    assert respuesta.json()["detalle"] == ""


def test_el_nombre_del_municipio_sale_del_catalogo(cliente_http, token_de):
    respuesta = crear(cliente_http, token_de(ANA), municipio_nombre="Otro nombre")
    assert respuesta.status_code == 201
    assert respuesta.json()["municipio_nombre"] == "Bogotá D.C."


def test_listar_mis_direcciones(cliente_http, token_de):
    crear(cliente_http, token_de(ANA))
    crear(
        cliente_http,
        token_de(ANA),
        departamento_codigo="05",
        municipio_codigo="05001",
        direccion="Carrera 70 # 1-20",
        detalle="",
    )
    respuesta = cliente_http.get("/mis-direcciones", headers=token_de(ANA))
    assert respuesta.status_code == 200
    assert [d["id"] for d in respuesta.json()] == [1, 2]
    assert [d["municipio_codigo"] for d in respuesta.json()] == ["11001", "05001"]


def test_un_cliente_sin_direcciones_recibe_lista_vacia(cliente_http, token_de):
    assert cliente_http.get("/mis-direcciones", headers=token_de(ANA)).json() == []


@pytest.mark.parametrize(
    "telefono", ["300123456", "30012345678", "2001234567", "abcdefghij", "300 123 4567", ""]
)
def test_telefono_no_valido_responde_422(cliente_http, token_de, telefono):
    assert crear(cliente_http, token_de(ANA), telefono=telefono).status_code == 422


def test_municipio_inexistente_responde_422(cliente_http, token_de):
    respuesta = crear(cliente_http, token_de(ANA), municipio_codigo="11999")
    assert respuesta.status_code == 422
    assert cliente_http.get("/mis-direcciones", headers=token_de(ANA)).json() == []


def test_municipio_de_otro_departamento_responde_422(cliente_http, token_de):
    respuesta = crear(cliente_http, token_de(ANA), departamento_codigo="05")
    assert respuesta.status_code == 422
    assert "municipio" in respuesta.json()["detail"]


@pytest.mark.parametrize(
    "cambios",
    [
        {"municipio_codigo": "abc"},
        {"departamento_codigo": "1"},
        {"nombre_recibe": "A"},
        {"direccion": "x"},
        {"direccion": "Calle 1\nCarrera 2"},
        {"detalle": "Apto\n302"},
        {"campo_extra": "no permitido"},
    ],
)
def test_datos_mal_formados_responden_422(cliente_http, token_de, cambios):
    assert crear(cliente_http, token_de(ANA), **cambios).status_code == 422


def test_faltan_campos_obligatorios_responde_422(cliente_http, token_de):
    cuerpo = {k: v for k, v in DIRECCION.items() if k != "municipio_codigo"}
    respuesta = cliente_http.post("/mis-direcciones", json=cuerpo, headers=token_de(ANA))
    assert respuesta.status_code == 422


def test_rn10_un_cliente_no_ve_las_direcciones_de_otro(cliente_http, token_de):
    crear(cliente_http, token_de(ANA))
    assert cliente_http.get("/mis-direcciones", headers=token_de(LUIS)).json() == []
    crear(cliente_http, token_de(LUIS), nombre_recibe="Luis Gómez")
    de_ana = cliente_http.get("/mis-direcciones", headers=token_de(ANA)).json()
    de_luis = cliente_http.get("/mis-direcciones", headers=token_de(LUIS)).json()
    assert [d["nombre_recibe"] for d in de_ana] == ["Ana Pérez"]
    assert [d["nombre_recibe"] for d in de_luis] == ["Luis Gómez"]


def test_rn10_consultar_una_direccion_propia(cliente_http, token_de):
    creada = crear(cliente_http, token_de(ANA)).json()
    respuesta = cliente_http.get(f"/mis-direcciones/{creada['id']}", headers=token_de(ANA))
    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_rn10_una_direccion_ajena_responde_404(cliente_http, token_de):
    creada = crear(cliente_http, token_de(ANA)).json()
    ajena = cliente_http.get(f"/mis-direcciones/{creada['id']}", headers=token_de(LUIS))
    inexistente = cliente_http.get("/mis-direcciones/999", headers=token_de(LUIS))
    assert ajena.status_code == 404
    assert inexistente.status_code == 404
    assert ajena.json()["detail"].replace(str(creada["id"]), "N") == inexistente.json()[
        "detail"
    ].replace("999", "N")


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [("get", "/mis-direcciones"), ("post", "/mis-direcciones"), ("get", "/mis-direcciones/1")],
)
def test_sin_token_responde_401(cliente_http, metodo, ruta):
    llamada = getattr(cliente_http, metodo)
    respuesta = llamada(ruta, json=DIRECCION) if metodo == "post" else llamada(ruta)
    assert respuesta.status_code == 401


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [("get", "/mis-direcciones"), ("post", "/mis-direcciones"), ("get", "/mis-direcciones/1")],
)
def test_un_asesor_responde_403(cliente_http, token_de, metodo, ruta):
    llamada = getattr(cliente_http, metodo)
    headers = token_de(ASESORA)
    respuesta = (
        llamada(ruta, json=DIRECCION, headers=headers)
        if metodo == "post"
        else llamada(ruta, headers=headers)
    )
    assert respuesta.status_code == 403


def test_token_invalido_responde_401(cliente_http):
    respuesta = cliente_http.get("/mis-direcciones", headers={"Authorization": "Bearer falso"})
    assert respuesta.status_code == 401
