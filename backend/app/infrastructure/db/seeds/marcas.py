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
        "nombre": "Yamaha",
        "color_hex": "#003399",
        "descripcion": DESC_YAMAHA,
    },
    {
        "nombre": "Honda",
        "color_hex": "#CC0000",
        "descripcion": DESC_HONDA,
    },
    {
        "nombre": "Kawasaki",
        "color_hex": "#00A650",
        "descripcion": DESC_KAWASAKI,
    },
]


def seed_marcas(db: Session) -> None:
    for datos in MARCAS_INICIALES:
        marca_existente = db.scalar(select(Marca).where(Marca.nombre.ilike(datos["nombre"])))
        if marca_existente is None:
            db.add(Marca(**datos))
