
from app.infrastructure.db.base import Base
from app.infrastructure.db.conexion import engine


def crear_tablas() -> None:
    Base.metadata.create_all(bind=engine)
