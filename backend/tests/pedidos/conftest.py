import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any

os.environ.setdefault("JWT_SECRET", "secreto-de-pruebas-con-mas-de-32-caracteres")

import pytest
from fastapi.testclient import TestClient

from app.api import dependencias
from app.config import ConfiguracionWompi
from app.domain.atencion import Rol, Usuario
from app.domain.excepciones import PasarelaNoDisponibleError
from app.infrastructure.externos.wompi import PasarelaWompi
from app.infrastructure.memoria.datos_prueba import asesores_iniciales
from app.infrastructure.memoria.pedidos import (
    RepositorioEnviosEnMemoria,
    RepositorioPagosEnMemoria,
    RepositorioPedidosEnMemoria,
)
from app.infrastructure.memoria.tienda import (
    RepositorioAccesoriosEnMemoria,
    RepositorioDireccionesEnMemoria,
    RepositorioUbicacionesEnMemoria,
)
from app.infrastructure.memoria.usuarios import RepositorioUsuariosEnMemoria
from app.infrastructure.seguridad.jwt_emisor import EmisorTokensJWT
from app.main import app
from tests.datos_accesorios import accesorios_de_prueba
from tests.tienda.conftest import DIRECCION

ZONA = timezone(timedelta(hours=-5), "COT")
INICIO = datetime(2026, 11, 15, 20, 0, 0, tzinfo=ZONA)
CONFIGURACION_WOMPI = ConfiguracionWompi(
    api_url="https://sandbox.wompi.test/v1",
    llave_publica="pub_test_llave_de_pruebas",
    secreto_integridad="secreto_integridad_de_pruebas",
    secreto_eventos="secreto_eventos_de_pruebas",
)
ANA = "ana@correo.com"
LUIS = "luis@correo.com"
ASESORA = "laura.ruiz@candela.com"
CASCO = 1
CHAQUETA = 3
COSTO_ENVIO_BOGOTA = 9_000


class RelojControlado:
    def __init__(self) -> None:
        self.ahora = INICIO

    def __call__(self) -> datetime:
        return self.ahora

    def avanzar(self, minutos: int) -> None:
        self.ahora += timedelta(minutes=minutos)


class TransporteWompiFalso:
    def __init__(self) -> None:
        self.transacciones: dict[str, dict[str, Any]] = {}
        self.consultas: list[str] = []
        self.caido = False

    def __call__(self, url: str) -> dict[str, Any]:
        self.consultas.append(url)
        if self.caido:
            raise PasarelaNoDisponibleError("Wompi no responde")
        identificador = url.rsplit("/", 1)[-1]
        return {"data": self.transacciones[identificador]}

    def registrar(self, identificador: str, referencia: str, estado: str, monto_cop: int) -> None:
        self.transacciones[identificador] = transaccion(
            identificador, referencia, estado, monto_cop
        )


def transaccion(identificador: str, referencia: str, estado: str, monto_cop: int) -> dict[str, Any]:
    return {
        "id": identificador,
        "status": estado,
        "reference": referencia,
        "amount_in_cents": monto_cop * 100,
        "currency": "COP",
    }


def evento_firmado(
    transaccion_evento: dict[str, Any],
    secreto: str = CONFIGURACION_WOMPI.secreto_eventos,
    marca_de_tiempo: int = 1731700000,
) -> dict[str, Any]:
    propiedades = ["transaction.id", "transaction.status", "transaction.amount_in_cents"]
    valores = "".join(
        str(transaccion_evento[campo]) for campo in ("id", "status", "amount_in_cents")
    )
    checksum = hashlib.sha256(f"{valores}{marca_de_tiempo}{secreto}".encode()).hexdigest()
    return {
        "event": "transaction.updated",
        "data": {"transaction": transaccion_evento},
        "environment": "test",
        "signature": {"properties": propiedades, "checksum": checksum},
        "timestamp": marca_de_tiempo,
        "sent_at": "2026-11-15T20:05:00.000Z",
    }


def entregar(sustituto):
    return lambda: sustituto


@pytest.fixture
def usuarios():
    repositorio = RepositorioUsuariosEnMemoria()
    for asesor in asesores_iniciales("hash"):
        repositorio.guardar(asesor)
    for nombre, correo in (("Ana Pérez", ANA), ("Luis Gómez", LUIS)):
        repositorio.guardar(
            Usuario(
                nombre=nombre,
                correo=correo,
                telefono="3001234567",
                hash_contrasena="hash",
                rol=Rol.CLIENTE,
            )
        )
    return repositorio


@pytest.fixture
def emisor():
    return EmisorTokensJWT(os.environ["JWT_SECRET"], 60)


@pytest.fixture
def reloj():
    return RelojControlado()


@pytest.fixture
def transporte():
    return TransporteWompiFalso()


@pytest.fixture
def accesorios():
    return RepositorioAccesoriosEnMemoria(accesorios_de_prueba())


@pytest.fixture
def pagos():
    return RepositorioPagosEnMemoria()


@pytest.fixture
def envios():
    return RepositorioEnviosEnMemoria()


@pytest.fixture
def pedidos(accesorios):
    return RepositorioPedidosEnMemoria(accesorios)


@pytest.fixture
def pasarela(transporte):
    return PasarelaWompi(CONFIGURACION_WOMPI, transporte)


@pytest.fixture
def cliente_http(usuarios, emisor, reloj, accesorios, pedidos, pagos, envios, pasarela):
    ubicaciones = RepositorioUbicacionesEnMemoria()
    direcciones = RepositorioDireccionesEnMemoria()
    sustitutos = {
        dependencias.obtener_repositorio_accesorios: accesorios,
        dependencias.obtener_repositorio_ubicaciones: ubicaciones,
        dependencias.obtener_repositorio_direcciones: direcciones,
        dependencias.obtener_repositorio_usuarios: usuarios,
        dependencias.obtener_emisor_tokens: emisor,
        dependencias.obtener_repositorio_pedidos: pedidos,
        dependencias.obtener_repositorio_pagos: pagos,
        dependencias.obtener_repositorio_envios: envios,
        dependencias.obtener_pasarela_pago: pasarela,
        dependencias.obtener_reloj_atencion: reloj,
    }
    for dependencia, sustituto in sustitutos.items():
        app.dependency_overrides[dependencia] = entregar(sustituto)
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def token_de(usuarios, emisor):
    def token(correo):
        return {"Authorization": f"Bearer {emisor.emitir(usuarios.buscar_por_correo(correo))}"}

    return token


@pytest.fixture
def crear_direccion(cliente_http, token_de):
    def crear(correo=ANA, **cambios):
        respuesta = cliente_http.post(
            "/mis-direcciones", json={**DIRECCION, **cambios}, headers=token_de(correo)
        )
        assert respuesta.status_code == 201
        return respuesta.json()["id"]

    return crear


@pytest.fixture
def crear_pedido(cliente_http, token_de, crear_direccion):
    def crear(correo=ANA, items=None, direccion_id=None):
        cuerpo = {
            "direccion_id": direccion_id or crear_direccion(correo),
            "items": items or [{"accesorio_id": CASCO, "cantidad": 2}],
        }
        return cliente_http.post("/pedidos", json=cuerpo, headers=token_de(correo))

    return crear
