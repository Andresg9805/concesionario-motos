import pytest

from app.domain.tienda import CategoriaAccesorio

CAMPOS = {
    "id",
    "sku",
    "nombre",
    "categoria",
    "descripcion",
    "precio_cop",
    "stock",
    "imagen_url",
}


def test_listar_accesorios_devuelve_el_catalogo_completo(cliente_http):
    respuesta = cliente_http.get("/accesorios")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 12
    assert all(set(accesorio) == CAMPOS for accesorio in cuerpo)
    assert [accesorio["id"] for accesorio in cuerpo] == sorted(a["id"] for a in cuerpo)


def test_el_catalogo_cubre_las_siete_categorias(cliente_http):
    categorias = {accesorio["categoria"] for accesorio in cliente_http.get("/accesorios").json()}
    assert categorias == {categoria.value for categoria in CategoriaAccesorio}


@pytest.mark.parametrize("categoria", [categoria.value for categoria in CategoriaAccesorio])
def test_filtrar_accesorios_por_categoria(cliente_http, categoria):
    respuesta = cliente_http.get("/accesorios", params={"categoria": categoria})
    assert respuesta.status_code == 200
    assert respuesta.json()
    assert {accesorio["categoria"] for accesorio in respuesta.json()} == {categoria}


def test_filtrar_accesorios_por_moto(cliente_http):
    respuesta = cliente_http.get("/accesorios", params={"moto_id": 8})
    skus = {accesorio["sku"] for accesorio in respuesta.json()}
    assert "MAL-002" in skus
    assert "MAL-001" not in skus
    assert "CAS-001" in skus


def test_filtrar_accesorios_por_categoria_y_moto(cliente_http):
    respuesta = cliente_http.get("/accesorios", params={"categoria": "CASCO", "moto_id": 3})
    assert [accesorio["sku"] for accesorio in respuesta.json()] == ["CAS-001", "CAS-002"]
    respuesta = cliente_http.get("/accesorios", params={"categoria": "MALETA", "moto_id": 3})
    assert [accesorio["sku"] for accesorio in respuesta.json()] == ["MAL-001"]


def test_filtrar_por_moto_sin_accesorios_devuelve_lista_vacia(cliente_http):
    respuesta = cliente_http.get("/accesorios", params={"moto_id": 9999})
    assert respuesta.status_code == 200
    assert respuesta.json() == []


@pytest.mark.parametrize(
    "params",
    [{"categoria": "SCOOTER"}, {"categoria": "casco"}, {"moto_id": 0}, {"moto_id": "abc"}],
)
def test_filtros_no_validos_responden_422(cliente_http, params):
    assert cliente_http.get("/accesorios", params=params).status_code == 422


def test_obtener_accesorio_por_id(cliente_http):
    respuesta = cliente_http.get("/accesorios/1")
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": 1,
        "sku": "CAS-001",
        "nombre": "Casco integral ECE 22.06",
        "categoria": "CASCO",
        "descripcion": "Doble visor, cierre micrométrico.",
        "precio_cop": 489000,
        "stock": 12,
        "imagen_url": "",
    }


def test_obtener_accesorio_inexistente_responde_404(cliente_http):
    respuesta = cliente_http.get("/accesorios/9999")
    assert respuesta.status_code == 404
    assert "9999" in respuesta.json()["detail"]


def test_obtener_accesorio_con_id_no_valido_responde_422(cliente_http):
    assert cliente_http.get("/accesorios/0").status_code == 422
    assert cliente_http.get("/accesorios/abc").status_code == 422
