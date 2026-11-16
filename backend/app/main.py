from dotenv import load_dotenv

load_dotenv()

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencias import USA_SQLITE, crear_expirar_reservas
from app.api.routers import (
    accesorios,
    admin,
    asesor,
    atencion,
    auth,
    direcciones,
    marcas,
    motos,
    pedidos,
    ubicaciones,
)
from app.api.tareas import ciclo_expirar_reservas
from app.infrastructure.db.inicializacion import preparar_base_de_datos


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI) -> AsyncIterator[None]:
    if USA_SQLITE:
        preparar_base_de_datos()
    tarea = asyncio.create_task(ciclo_expirar_reservas(crear_expirar_reservas))
    try:
        yield
    finally:
        tarea.cancel()
        with suppress(asyncio.CancelledError):
            await tarea


app = FastAPI(
    title="Concesionario de Motos API",
    version="0.1.0",
    description="API del proyecto final de Taller de Programación - UMB",
    lifespan=ciclo_de_vida,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Sesion-Id"],
    expose_headers=["X-Sesion-Id"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(marcas.router)
app.include_router(motos.router)
app.include_router(atencion.router)
app.include_router(asesor.router)
app.include_router(accesorios.router)
app.include_router(ubicaciones.router)
app.include_router(direcciones.router)
app.include_router(pedidos.router_pedidos)
app.include_router(pedidos.router_mis_pedidos)
app.include_router(pedidos.router_webhooks)


@app.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    return {"status": "ok"}
