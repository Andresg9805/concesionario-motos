from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, marcas, motos

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
app.include_router(marcas.router)
app.include_router(motos.router)


@app.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    return {"status": "ok"}
