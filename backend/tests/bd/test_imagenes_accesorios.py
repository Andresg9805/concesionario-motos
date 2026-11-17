from pathlib import Path

from sqlalchemy import select

from app.infrastructure.db.seeds.accesorios import ACCESORIOS_INICIALES, seed_accesorios
from app.infrastructure.models import Accesorio

CARPETA_PUBLICA = Path(__file__).resolve().parents[3] / "frontend" / "public"


def test_cada_accesorio_apunta_a_su_foto_con_el_sku():
    for datos in ACCESORIOS_INICIALES:
        esperado = f"/accesorios/{datos['sku'].lower()}.webp"
        assert datos["imagen_url"] == esperado
        assert (CARPETA_PUBLICA / esperado.lstrip("/")).is_file()


def test_la_base_de_datos_guarda_la_foto_del_accesorio(sesion):
    seed_accesorios(sesion)
    sesion.flush()
    casco = sesion.scalar(select(Accesorio).where(Accesorio.sku == "SHO-CAS-001"))
    assert casco.imagen_url == "/accesorios/sho-cas-001.webp"


def test_completa_las_fotos_de_una_base_vieja_sin_tocar_las_del_administrador(sesion):
    seed_accesorios(sesion)
    sesion.flush()
    for accesorio in sesion.scalars(select(Accesorio)):
        accesorio.imagen_url = ""
    casco = sesion.scalar(select(Accesorio).where(Accesorio.sku == "SHO-CAS-001"))
    casco.imagen_url = "https://ejemplo.com/casco.jpg"
    sesion.flush()

    seed_accesorios(sesion)
    sesion.flush()

    vacias = sesion.scalars(select(Accesorio.sku).where(Accesorio.imagen_url == "")).all()
    assert vacias == []
    assert casco.imagen_url == "https://ejemplo.com/casco.jpg"
    assert sesion.scalar(select(Accesorio).where(Accesorio.sku == "ALP-GUA-001")).imagen_url == (
        "/accesorios/alp-gua-001.webp"
    )
