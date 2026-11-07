# Candela Motors

**Calidad japonesa.** Página web de un concesionario de motos japonesas: Honda, Kawasaki y Yamaha. Es el proyecto final de **Taller de Programación** en la Universidad Manuela Beltrán (UMB), segundo semestre de 2026.

No es una página folleto. Candela Motors ayuda a decidir con números reales y acompaña al cliente:

- **Buscar por cuota:** dices cuánto puedes pagar al mes y qué licencia tienes (A1 o A2), y la página te muestra las motos que te alcanzan.
- **Costo real mensual:** cuota, gasolina, SOAT, mantenimiento e impuesto, según cómo uses la moto. Con un modo trabajo para domiciliarios que muestra en cuántos meses se paga.
- **Atención personalizada:** al cotizar o pedir un test drive te asignamos un asesor especialista en la marca y te damos un código para seguir tu atención, sin crear cuenta.
- **Tienda de accesorios:** cascos, chaquetas y más, con pago virtual (Wompi en ambiente de pruebas) y seguimiento del envío.
- **Radar de demanda:** el administrador ve qué busca la gente frente al inventario que tiene.

El alcance completo, las reglas de negocio, el modelo de datos y la API están en [docs/alcance.md](docs/alcance.md).

**Fecha de entrega:** martes 17 de noviembre de 2026

## Equipo

| Integrante | Usuario de GitHub | Rol |
| --- | --- | --- |
| Andrés Guillermo Velasco Candela | [@Andresg9805](https://github.com/Andresg9805) | Líder del proyecto, dominio y frontend |
| Laura Camila González Martínez | [@Camila2212](https://github.com/Camila2212) | Base de datos y pruebas |
| Nicolás Esteban Bello Martínez | [@SixExpert277](https://github.com/SixExpert277) | Requisitos y API |

**Docente:** Kevin Andrés Quintero Córdoba

## Tecnologías

| Parte | Tecnología |
| --- | --- |
| Backend | Python, FastAPI |
| Arquitectura | Hexagonal (dominio, aplicación, infraestructura, API) |
| Base de datos | SQLAlchemy 2.0 con SQLite en desarrollo |
| Reportes | DuckDB |
| Seguridad | JWT con roles (cliente, asesor y administrador) |
| Pagos | Wompi en ambiente de pruebas (sandbox) |
| Datos abiertos | TRM y DIVIPOLA de datos.gov.co |
| Frontend | Angular |
| Calidad | pytest, ruff, mypy, mutmut |
| Despliegue | Docker y GitHub Actions |

## Estructura del proyecto

```
concesionario-motos/
├── backend/
│   ├── app/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── api/
│   └── tests/
├── frontend/
├── docs/
│   ├── requisitos/
│   ├── uml/
│   ├── wireframes/
│   ├── calidad/
│   ├── evidencias/
│   └── informe/
└── .github/
```

## Cómo correr el backend

Desde la carpeta `backend`:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

En Mac o Linux el segundo comando es `source .venv/bin/activate`.

Con el servidor andando, la documentación de la API queda en http://localhost:8000/docs

Para correr las pruebas y el análisis estático:

```
pytest
ruff check .
```

## Cómo trabajamos

Toda la forma de trabajo con Git y GitHub está en [CONTRIBUTING.md](CONTRIBUTING.md). Las tareas están en la pestaña **Projects** de este repositorio, en el tablero **Concesionario Motos**.
