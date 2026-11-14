from app.infrastructure.db.conexion import SessionLocal
from app.infrastructure.db.seeds.accesorios import seed_accesorios
from app.infrastructure.db.seeds.marcas import seed_marcas
from app.infrastructure.db.seeds.motos_honda import seed_motos_honda
from app.infrastructure.db.seeds.motos_kawasaki import seed_motos_kawasaki
from app.infrastructure.db.seeds.motos_yamaha import seed_motos_yamaha


def ejecutar_seeds() -> None:
    db = SessionLocal()

    try:
        seed_marcas(db)
        seed_motos_kawasaki(db)
        seed_motos_honda(db)
        seed_motos_yamaha(db)
        seed_accesorios(db)
        
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
