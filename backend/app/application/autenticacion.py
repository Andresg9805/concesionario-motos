from dataclasses import dataclass

from app.domain.atencion import Cliente, Rol, Usuario
from app.domain.excepciones import CorreoYaRegistradoError, CredencialesInvalidasError
from app.domain.puertos import RepositorioClientes, RepositorioUsuarios
from app.domain.seguridad import EmisorTokens, HasheadorContrasenas

MENSAJE_CORREO_REGISTRADO = "Ya existe una cuenta con ese correo"
MENSAJE_CREDENCIALES_INVALIDAS = "Correo o contraseña incorrectos"


@dataclass(frozen=True)
class DatosRegistro:
    nombre: str
    correo: str
    celular: str
    contrasena: str


class RegistrarCliente:
    def __init__(
        self,
        usuarios: RepositorioUsuarios,
        clientes: RepositorioClientes,
        hasheador: HasheadorContrasenas,
    ) -> None:
        self._usuarios = usuarios
        self._clientes = clientes
        self._hasheador = hasheador

    def ejecutar(self, datos: DatosRegistro) -> Usuario:
        correo = datos.correo.strip().lower()
        if self._usuarios.buscar_por_correo(correo) is not None:
            raise CorreoYaRegistradoError(MENSAJE_CORREO_REGISTRADO)
        usuario = self._usuarios.guardar(
            Usuario(
                nombre=datos.nombre.strip(),
                correo=correo,
                telefono=datos.celular,
                hash_contrasena=self._hasheador.hashear(datos.contrasena),
                rol=Rol.CLIENTE,
            )
        )
        self._clientes.guardar(
            Cliente(
                nombre=usuario.nombre,
                correo=usuario.correo,
                telefono=usuario.telefono,
                usuario=usuario,
            )
        )
        return usuario


class IniciarSesion:
    def __init__(
        self,
        usuarios: RepositorioUsuarios,
        hasheador: HasheadorContrasenas,
        emisor: EmisorTokens,
        hash_senuelo: str,
    ) -> None:
        self._usuarios = usuarios
        self._hasheador = hasheador
        self._emisor = emisor
        self._hash_senuelo = hash_senuelo

    def ejecutar(self, correo: str, contrasena: str) -> str:
        usuario = self._usuarios.buscar_por_correo(correo.strip().lower())
        hash_guardado = usuario.hash_contrasena if usuario else self._hash_senuelo
        valida = self._hasheador.verificar(contrasena, hash_guardado)
        if usuario is None or not valida:
            raise CredencialesInvalidasError(MENSAJE_CREDENCIALES_INVALIDAS)
        return self._emisor.emitir(usuario)
