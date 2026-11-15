import app.infrastructure.models  # noqa: F401
from app.infrastructure.db.base import Base
from app.infrastructure.db.conexion import engine
from app.infrastructure.db.seeds import ejecutar_seeds


def crear_tablas() -> None:
    Base.metadata.create_all(bind=engine)
    ejecutar_seeds()
