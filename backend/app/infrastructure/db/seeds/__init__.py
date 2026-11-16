def ejecutar_seeds() -> None:
    from app.infrastructure.db.conexion import SessionLocal
    from app.infrastructure.db.seeds.accesorios import seed_accesorios
    from app.infrastructure.db.seeds.catalogos import seed_catalogos
    from app.infrastructure.db.seeds.marcas import seed_marcas
    from app.infrastructure.db.seeds.motos import seed_motos
    from app.infrastructure.db.seeds.parametros_costo import seed_parametros_costo
    from app.infrastructure.db.seeds.ubicaciones import seed_ubicaciones
    from app.infrastructure.db.seeds.usuarios import seed_usuarios

    db = SessionLocal()

    try:
        seed_catalogos(db)
        seed_marcas(db)
        db.flush()
        seed_usuarios(db)
        seed_motos(db)
        seed_accesorios(db)
        seed_parametros_costo(db)
        seed_ubicaciones(db)

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
