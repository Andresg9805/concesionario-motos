from pathlib import Path

from sqlalchemy import select

from app.infrastructure.db.seeds.marcas import seed_marcas
from app.infrastructure.db.seeds.motos import MOTOS_POR_MARCA, seed_motos
from app.infrastructure.models import Marca, Moto

CARPETA_PUBLICA = Path(__file__).resolve().parents[3] / "frontend" / "public"


def cargar_motos(sesion):
    seed_marcas(sesion)
    sesion.flush()
    seed_motos(sesion)
    sesion.flush()


def moto_de_la_semilla(modelo):
    for nombre_marca, lista in MOTOS_POR_MARCA:
        for datos in lista:
            if datos["modelo"] == modelo:
                return nombre_marca, datos
    raise AssertionError(modelo)


def test_cada_moto_de_la_semilla_apunta_a_una_foto_que_existe():
    for _, lista in MOTOS_POR_MARCA:
        for datos in lista:
            assert datos["imagen_url"].startswith("/motos/"), datos["modelo"]
            assert (CARPETA_PUBLICA / datos["imagen_url"].lstrip("/")).is_file()


def test_la_base_de_datos_guarda_la_ruta_de_la_foto(sesion):
    cargar_motos(sesion)
    r3 = sesion.scalar(select(Moto).where(Moto.modelo == "R3"))
    assert r3.imagen_url == "/motos/yamaha/r3.webp"


def test_completa_la_foto_de_una_base_que_ya_tenia_las_motos_sin_imagen(sesion):
    cargar_motos(sesion)
    for moto in sesion.scalars(select(Moto)):
        moto.imagen_url = ""
    sesion.flush()

    seed_motos(sesion)
    sesion.flush()

    vacias = sesion.scalars(select(Moto.modelo).where(Moto.imagen_url == "")).all()
    assert vacias == []


def test_no_cambia_una_imagen_que_puso_el_administrador(sesion):
    cargar_motos(sesion)
    nombre_marca, datos = moto_de_la_semilla("R3")
    marca = sesion.scalar(select(Marca).where(Marca.nombre == nombre_marca))
    r3 = sesion.scalar(select(Moto).where(Moto.marca_id == marca.id, Moto.modelo == "R3"))
    r3.imagen_url = "https://ejemplo.com/r3-azul.jpg"
    sesion.flush()

    seed_motos(sesion)
    sesion.flush()

    assert r3.imagen_url == "https://ejemplo.com/r3-azul.jpg"
    assert datos["imagen_url"] == "/motos/yamaha/r3.webp"
