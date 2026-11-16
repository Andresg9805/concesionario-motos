import os

os.environ.setdefault("JWT_SECRET", "secreto-de-pruebas-con-mas-de-32-caracteres")

import pytest
from fastapi.testclient import TestClient

from app.api import dependencias
from app.domain.atencion import Rol, Usuario
from app.infrastructure.externos.wompi import PasarelaWompi
from app.infrastructure.memoria.catalogo import (
    RepositorioMarcasEnMemoria,
    RepositorioMotosEnMemoria,
    RepositorioParametrosEnMemoria,
)
from app.infrastructure.memoria.datos_prueba import administrador_inicial, asesores_iniciales
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
from tests.pedidos.conftest import (
    CONFIGURACION_WOMPI,
    RelojControlado,
    TransporteWompiFalso,
    evento_firmado,
    transaccion,
)
from tests.tienda.conftest import DIRECCION

ADMIN = "admin@candela.com"
ASESORA = "laura.ruiz@candela.com"
CLIENTE = "ana@correo.com"
CASCO = 1


def entregar(sustituto):
    return lambda: sustituto


@pytest.fixture
def usuarios():
    repositorio = RepositorioUsuariosEnMemoria()
    for asesor in asesores_iniciales("hash"):
        repositorio.guardar(asesor)
    repositorio.guardar(administrador_inicial("hash"))
    repositorio.guardar(
        Usuario(
            nombre="Ana Pérez",
            correo=CLIENTE,
            telefono="3001234567",
            hash_contrasena="hash",
            rol=Rol.CLIENTE,
        )
    )
    return repositorio


@pytest.fixture
def motos():
    return RepositorioMotosEnMemoria()


@pytest.fixture
def accesorios():
    return RepositorioAccesoriosEnMemoria(accesorios_de_prueba())


@pytest.fixture
def parametros():
    return RepositorioParametrosEnMemoria()


@pytest.fixture
def envios():
    return RepositorioEnviosEnMemoria()


@pytest.fixture
def cliente_http(usuarios, motos, accesorios, parametros, envios):
    emisor = EmisorTokensJWT(os.environ["JWT_SECRET"], 60)
    reloj = RelojControlado()
    transporte = TransporteWompiFalso()
    pagos = RepositorioPagosEnMemoria()
    pedidos = RepositorioPedidosEnMemoria(accesorios)
    sustitutos = {
        dependencias.obtener_repositorio_usuarios: usuarios,
        dependencias.obtener_repositorio_motos: motos,
        dependencias.obtener_repositorio_marcas: RepositorioMarcasEnMemoria(),
        dependencias.obtener_repositorio_accesorios: accesorios,
        dependencias.obtener_repositorio_parametros: parametros,
        dependencias.obtener_repositorio_ubicaciones: RepositorioUbicacionesEnMemoria(),
        dependencias.obtener_repositorio_direcciones: RepositorioDireccionesEnMemoria(),
        dependencias.obtener_repositorio_pedidos: pedidos,
        dependencias.obtener_repositorio_pagos: pagos,
        dependencias.obtener_repositorio_envios: envios,
        dependencias.obtener_pasarela_pago: PasarelaWompi(CONFIGURACION_WOMPI, transporte),
        dependencias.obtener_emisor_tokens: emisor,
        dependencias.obtener_reloj_atencion: reloj,
    }
    for dependencia, sustituto in sustitutos.items():
        app.dependency_overrides[dependencia] = entregar(sustituto)
    cliente = TestClient(app)
    cliente.emisor = emisor
    cliente.transporte = transporte
    cliente.reloj = reloj
    yield cliente
    app.dependency_overrides.clear()


@pytest.fixture
def token_de(usuarios, cliente_http):
    def token(correo):
        usuario = usuarios.buscar_por_correo(correo)
        return {"Authorization": f"Bearer {cliente_http.emisor.emitir(usuario)}"}

    return token


@pytest.fixture
def admin(token_de):
    return token_de(ADMIN)


@pytest.fixture
def pedido_pagado(cliente_http, token_de):
    def crear():
        direccion = cliente_http.post(
            "/mis-direcciones", json=DIRECCION, headers=token_de(CLIENTE)
        ).json()["id"]
        creado = cliente_http.post(
            "/pedidos",
            json={"direccion_id": direccion, "items": [{"accesorio_id": CASCO, "cantidad": 2}]},
            headers=token_de(CLIENTE),
        ).json()
        referencia = creado["wompi"]["referencia"]
        monto = creado["total_cop"]
        evento = transaccion("tx-1", referencia, "APPROVED", monto)
        cliente_http.post("/webhooks/wompi", json=evento_firmado(evento))
        return creado["pedido_id"]

    return crear
