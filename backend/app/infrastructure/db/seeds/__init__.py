from app.infrastructure.db.conexion import SessionLocal
from app.infrastructure.db.seeds.accesorios import seed_accesorios
from app.infrastructure.db.seeds.catalogos import seed_catalogos
from app.infrastructure.db.seeds.marcas import seed_marcas
from app.infrastructure.db.seeds.motos import seed_motos


def ejecutar_seeds() -> None:
    db = SessionLocal()

    try:
        seed_catalogos(db)
        seed_marcas(db)
        db.flush()
        seed_motos(db)
        seed_accesorios(db)

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
