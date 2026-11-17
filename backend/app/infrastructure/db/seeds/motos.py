from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.seeds.motos_honda import MOTOS_HONDA
from app.infrastructure.db.seeds.motos_kawasaki import MOTOS_KAWASAKI
from app.infrastructure.db.seeds.motos_yamaha import MOTOS_YAMAHA
from app.infrastructure.models.marca import Marca
from app.infrastructure.models.moto import Moto
from app.infrastructure.models.tipo_moto import TipoMoto

MOTOS_POR_MARCA: tuple[tuple[str, list[dict[str, Any]]], ...] = (
    ("Honda", MOTOS_HONDA),
    ("Kawasaki", MOTOS_KAWASAKI),
    ("Yamaha", MOTOS_YAMAHA),
)


def seed_motos(db: Session) -> None:
    tipos = {tipo.clave: tipo.id for tipo in db.scalars(select(TipoMoto))}
    for nombre_marca, lista in MOTOS_POR_MARCA:
        marca = db.scalar(select(Marca).where(Marca.nombre == nombre_marca))
        if marca is None:
            continue
        for datos in lista:
            existente = db.scalar(
                select(Moto).where(
                    Moto.marca_id == marca.id,
                    Moto.modelo == datos["modelo"],
                    Moto.anio == datos["anio"],
                )
            )
            if existente is None:
                columnas = {clave: valor for clave, valor in datos.items() if clave != "tipo"}
                db.add(Moto(**columnas, marca_id=marca.id, tipo_id=tipos[datos["tipo"]]))
            elif not existente.imagen_url and datos["imagen_url"]:
                existente.imagen_url = datos["imagen_url"]
