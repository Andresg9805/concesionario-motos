from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.categoria_accesorio import CategoriaAccesorio
from app.infrastructure.models.fabricante import Fabricante
from app.infrastructure.models.tipo_moto import TipoMoto

TIPOS_MOTO: tuple[tuple[str, str], ...] = (
    ("NAKED", "Naked"),
    ("DOBLE_PROPOSITO", "Doble propósito"),
    ("TRAIL", "Trail"),
    ("DEPORTIVA", "Deportiva"),
)

CATEGORIAS_ACCESORIO: tuple[tuple[str, str], ...] = (
    ("CASCO", "Cascos"),
    ("CHAQUETA", "Chaquetas"),
    ("GUANTES", "Guantes"),
    ("RODILLERA", "Rodilleras"),
    ("HOMBRERA", "Hombreras"),
    ("MALETA", "Maletas"),
    ("MANTENIMIENTO", "Mantenimiento"),
)

FABRICANTES: tuple[str, ...] = (
    "Alpinestars",
    "GIVI",
    "Honda",
    "Kawasaki",
    "SAS-TEC",
    "SHOEI",
    "Yamaha",
)


def seed_catalogos(db: Session) -> None:
    for clave, nombre in TIPOS_MOTO:
        if db.scalar(select(TipoMoto).where(TipoMoto.clave == clave)) is None:
            db.add(TipoMoto(clave=clave, nombre=nombre))
    for clave, nombre in CATEGORIAS_ACCESORIO:
        if db.scalar(select(CategoriaAccesorio).where(CategoriaAccesorio.clave == clave)) is None:
            db.add(CategoriaAccesorio(clave=clave, nombre=nombre))
    for nombre in FABRICANTES:
        if db.scalar(select(Fabricante).where(Fabricante.nombre == nombre)) is None:
            db.add(Fabricante(nombre=nombre))
