from sqlalchemy import Engine, inspect, text

import app.infrastructure.models  # noqa: F401
from app.infrastructure.db.base import Base
from app.infrastructure.db.conexion import engine
from app.infrastructure.db.seeds import ejecutar_seeds
from app.infrastructure.memoria.datos_prueba import parametros_iniciales


def columnas_agregadas_despues() -> dict[str, dict[str, str]]:
    iniciales = parametros_iniciales()
    return {
        "parametros_costo": {
            "valor_matricula_cop": f"INTEGER NOT NULL DEFAULT {iniciales.valor_matricula_cop}",
            "valor_tramites_cop": f"INTEGER NOT NULL DEFAULT {iniciales.valor_tramites_cop}",
            "tasa_mensual": f"NUMERIC(6, 4) NOT NULL DEFAULT {iniciales.tasa_mensual}",
        },
        "busquedas": {
            "categoria_licencia": "VARCHAR(2) NOT NULL DEFAULT 'A2'",
        },
    }


def agregar_columnas_faltantes(motor: Engine) -> list[str]:
    inspector = inspect(motor)
    tablas = set(inspector.get_table_names())
    agregadas: list[str] = []
    with motor.begin() as conexion:
        for tabla, columnas in columnas_agregadas_despues().items():
            if tabla not in tablas:
                continue
            existentes = {columna["name"] for columna in inspector.get_columns(tabla)}
            for nombre, definicion in columnas.items():
                if nombre not in existentes:
                    conexion.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {nombre} {definicion}"))
                    agregadas.append(f"{tabla}.{nombre}")
    return agregadas


def preparar_base_de_datos(motor: Engine = engine) -> None:
    Base.metadata.create_all(bind=motor)
    agregar_columnas_faltantes(motor)
    ejecutar_seeds()


def crear_tablas() -> None:
    preparar_base_de_datos()
