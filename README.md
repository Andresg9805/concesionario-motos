# Concesionario de Motos

Página web de un concesionario de motos. Es el proyecto final de **Taller de Programación** en la Universidad Manuela Beltrán (UMB), segundo semestre de 2026.

La página permite ver el catálogo de motos con filtros, ver el detalle de cada moto, pedir una cotización con simulador de crédito y agendar un test drive. Los asesores y el administrador entran con usuario y contraseña para manejar el inventario.

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
| Seguridad | JWT con roles |
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
