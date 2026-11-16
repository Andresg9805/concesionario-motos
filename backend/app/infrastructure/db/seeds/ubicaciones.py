
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.memoria.datos_ubicaciones import DEPARTAMENTOS, MUNICIPIOS
from app.infrastructure.models.departamento import Departamento
from app.infrastructure.models.municipio import Municipio


def seed_ubicaciones(db: Session) -> None:
    for codigo, nombre, costo, dias in DEPARTAMENTOS:
        departamento = db.get(Departamento, codigo)

        if departamento is None:
            db.add(
                Departamento(
                    codigo=codigo,
                    nombre=nombre,
                    costo_envio_cop=costo,
                    dias_envio=dias,
                )
            )
        else:
            departamento.nombre = nombre
            departamento.costo_envio_cop = costo
            departamento.dias_envio = dias

    db.flush()

    for codigo_departamento, municipios in MUNICIPIOS.items():
        for codigo, nombre in municipios:
            municipio = db.scalar(
                select(Municipio).where(Municipio.codigo == codigo)
            )

            if municipio is None:
                db.add(
                    Municipio(
                        codigo=codigo,
                        nombre=nombre,
                        departamento_codigo=codigo_departamento,
                    )
                )
            else:
                municipio.nombre = nombre
                municipio.departamento_codigo = codigo_departamento
