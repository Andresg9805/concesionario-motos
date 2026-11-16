from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app = FastAPI(
    title="Concesionario de Motos API",
    version="0.1.0",
    description="API del proyecto final de Taller de Programación - UMB",
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
