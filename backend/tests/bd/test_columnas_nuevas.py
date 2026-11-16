from sqlalchemy import create_engine, inspect, text

from app.infrastructure.db.inicializacion import agregar_columnas_faltantes


def motor_con_tablas_viejas(ruta):
    motor = create_engine(f"sqlite:///{ruta}")
    with motor.begin() as conexion:
        conexion.execute(
            text(
                "CREATE TABLE parametros_costo (id INTEGER PRIMARY KEY, precio_galon_cop INTEGER, "
                "porcentaje_impuesto NUMERIC(5, 2), actualizado_en DATETIME)"
            )
        )
        conexion.execute(
            text("INSERT INTO parametros_costo VALUES (1, 16200, 1.5, '2026-11-10 08:00:00')")
        )
        conexion.execute(
            text(
                "CREATE TABLE busquedas (id INTEGER PRIMARY KEY, fecha DATETIME, "
                "cuota_maxima_cop INTEGER, cuota_inicial_cop INTEGER, uso VARCHAR, "
                "marca_id INTEGER, cantidad_resultados INTEGER)"
            )
        )
        conexion.execute(
            text(
                "INSERT INTO busquedas VALUES (1, '2026-11-10 08:00:00', 300000, 0, 'CIUDAD', 1, 2)"
            )
        )
    return motor


def test_agrega_las_columnas_que_le_faltan_a_una_base_de_datos_vieja(tmp_path):
    motor = motor_con_tablas_viejas(tmp_path / "vieja.db")

    agregadas = agregar_columnas_faltantes(motor)

    assert sorted(agregadas) == [
        "busquedas.categoria_licencia",
        "parametros_costo.tasa_mensual",
        "parametros_costo.valor_matricula_cop",
        "parametros_costo.valor_tramites_cop",
    ]
    with motor.connect() as conexion:
        fila = conexion.execute(
            text(
                "SELECT valor_matricula_cop, valor_tramites_cop, tasa_mensual FROM parametros_costo"
            )
        ).one()
        licencia = conexion.execute(text("SELECT categoria_licencia FROM busquedas")).scalar_one()
    assert (fila[0], fila[1], float(fila[2])) == (520_000, 380_000, 0.0179)
    assert licencia == "A2"


def test_correrlo_otra_vez_no_cambia_nada(tmp_path):
    motor = motor_con_tablas_viejas(tmp_path / "vieja.db")
    agregar_columnas_faltantes(motor)

    assert agregar_columnas_faltantes(motor) == []
    columnas = {c["name"] for c in inspect(motor).get_columns("busquedas")}
    assert "categoria_licencia" in columnas


def test_si_la_tabla_no_existe_no_hace_nada(tmp_path):
    motor = create_engine(f"sqlite:///{tmp_path / 'vacia.db'}")

    assert agregar_columnas_faltantes(motor) == []
