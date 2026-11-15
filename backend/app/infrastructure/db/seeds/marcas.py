from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models.marca import Marca

DESC_YAMAHA = (
    "Reconocido fabricante japonés de motocicletas, "
    "destacado por su innovación tecnológica, alto desempeño "
    "y amplia trayectoria en el mercado global."
)

DESC_HONDA = (
    "Líder mundial en ingeniería japonesa, especializado "
    "en la fabricación de motocicletas confiables, duraderas "
    "y de alta eficiencia para todo tipo de usuario."
)

DESC_KAWASAKI = (
    "Emblemático fabricante japonés de motocicletas, "
    "famoso por su ingeniería de alto rendimiento, potencia "
    "inigualable y diseño deportivo de vanguardia."
)

MARCAS_INICIALES: list[dict[str, Any]] = [
    {
        "nombre": "Honda",
        "color_hex": "#CC0000",
        "descripcion": DESC_HONDA,
    },
    {
        "nombre": "Kawasaki",
        "color_hex": "#66CC33",
        "descripcion": DESC_KAWASAKI,
    },
    {
        "nombre": "Yamaha",
        "color_hex": "#0033A0",
        "descripcion": DESC_YAMAHA,
    },
]


def seed_marcas(db: Session) -> None:
    for datos in MARCAS_INICIALES:
        if db.scalar(select(Marca).where(Marca.nombre == datos["nombre"])) is None:
            db.add(Marca(**datos))
