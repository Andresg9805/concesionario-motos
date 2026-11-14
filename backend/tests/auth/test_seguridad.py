from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.application.autenticacion import DatosRegistro, IniciarSesion, RegistrarCliente
from app.domain.atencion import Rol, Usuario
from app.domain.excepciones import (
    CorreoYaRegistradoError,
    CredencialesInvalidasError,
    TokenInvalidoError,
)
from app.infrastructure.seguridad.bcrypt_hasheador import RONDAS_BCRYPT, HasheadorBcrypt
from app.infrastructure.seguridad.jwt_emisor import EmisorTokensJWT
from tests.auth.conftest import SECRETO

DATOS = DatosRegistro(
    nombre="Ana Pérez", correo="Ana@Correo.com", celular="3001234567", contrasena="clave1234"
)


def test_bcrypt_usa_12_rondas_por_defecto():
    hash_generado = HasheadorBcrypt().hashear("clave1234")

    assert RONDAS_BCRYPT == 12
    assert hash_generado.split("$")[2] == "12"


def test_bcrypt_verifica_y_rechaza(hasheador):
    hash_generado = hasheador.hashear("clave1234")

    assert hasheador.verificar("clave1234", hash_generado)
    assert not hasheador.verificar("clave12345", hash_generado)
    assert not hasheador.verificar("clave1234", "no-es-un-hash")


def test_registrar_cliente_siempre_crea_rol_cliente(usuarios, clientes, hasheador):
    usuario = RegistrarCliente(usuarios, clientes, hasheador).ejecutar(DATOS)

    assert usuario.id == 1
    assert usuario.rol == Rol.CLIENTE
    assert usuario.correo == "ana@correo.com"
    assert usuario.hash_contrasena != "clave1234"
    assert clientes.buscar_por_correo("ana@correo.com") is not None


def test_registrar_cliente_rechaza_correo_repetido(usuarios, clientes, hasheador):
    caso_de_uso = RegistrarCliente(usuarios, clientes, hasheador)
    caso_de_uso.ejecutar(DATOS)

    with pytest.raises(CorreoYaRegistradoError, match="Ya existe una cuenta con ese correo"):
        caso_de_uso.ejecutar(DATOS)


def test_iniciar_sesion_rechaza_credenciales(usuarios, clientes, hasheador, emisor):
    RegistrarCliente(usuarios, clientes, hasheador).ejecutar(DATOS)
    caso_de_uso = IniciarSesion(usuarios, hasheador, emisor, hasheador.hashear("x"))

    assert caso_de_uso.ejecutar("ana@correo.com", "clave1234")
    with pytest.raises(CredencialesInvalidasError):
        caso_de_uso.ejecutar("ana@correo.com", "mala")
    with pytest.raises(CredencialesInvalidasError):
        caso_de_uso.ejecutar("otro@correo.com", "clave1234")


def test_token_expira_segun_los_minutos_configurados():
    ahora = datetime(2026, 11, 12, 12, 0, tzinfo=UTC)
    emisor = EmisorTokensJWT(SECRETO, 60, reloj=lambda: ahora)
    usuario = Usuario(id=7, nombre="Ana", correo="a@b.co", hash_contrasena="h", rol=Rol.CLIENTE)

    payload = jwt.decode(
        emisor.emitir(usuario), SECRETO, algorithms=["HS256"], options={"verify_exp": False}
    )

    assert payload["exp"] == int((ahora + timedelta(minutes=60)).timestamp())


def test_token_vencido_es_invalido():
    pasado = datetime.now(UTC) - timedelta(hours=2)
    emisor = EmisorTokensJWT(SECRETO, 60, reloj=lambda: pasado)
    usuario = Usuario(id=7, nombre="Ana", correo="a@b.co", hash_contrasena="h", rol=Rol.CLIENTE)

    with pytest.raises(TokenInvalidoError):
        emisor.leer(emisor.emitir(usuario))


def test_token_con_otra_firma_o_algoritmo_none_es_invalido(emisor):
    payload = {"sub": "1", "nombre": "x", "rol": "ADMIN", "marca": None, "exp": 9999999999}
    falsificado = jwt.encode(payload, "otro-secreto-de-mas-de-32-caracteres!!", algorithm="HS256")
    sin_firma = jwt.encode(payload, None, algorithm="none")

    with pytest.raises(TokenInvalidoError):
        emisor.leer(falsificado)
    with pytest.raises(TokenInvalidoError):
        emisor.leer(sin_firma)
