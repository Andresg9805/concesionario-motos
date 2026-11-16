from dataclasses import dataclass

from app.domain.excepciones import DireccionInvalidaError, EntidadNoEncontradaError
from app.domain.puertos import (
    RepositorioAccesorios,
    RepositorioDirecciones,
    RepositorioUbicaciones,
    RepositorioUsuarios,
)
from app.domain.tienda import Accesorio, CategoriaAccesorio, Departamento, Direccion, Municipio

SEPARADOR_DETALLE = "\n"


class ListarAccesorios:
    def __init__(self, accesorios: RepositorioAccesorios) -> None:
        self._accesorios = accesorios

    def ejecutar(self, categoria: CategoriaAccesorio | None = None) -> list[Accesorio]:
        return sorted(self._accesorios.listar(categoria), key=lambda accesorio: accesorio.id or 0)


class ObtenerAccesorio:
    def __init__(self, accesorios: RepositorioAccesorios) -> None:
        self._accesorios = accesorios

    def ejecutar(self, accesorio_id: int) -> Accesorio:
        accesorio = self._accesorios.buscar_por_id(accesorio_id)
        if accesorio is None:
            raise EntidadNoEncontradaError(f"No existe un accesorio con id {accesorio_id}")
        return accesorio


class ListarDepartamentos:
    def __init__(self, ubicaciones: RepositorioUbicaciones) -> None:
        self._ubicaciones = ubicaciones

    def ejecutar(self) -> list[Departamento]:
        return self._ubicaciones.listar_departamentos()


class ObtenerDepartamento:
    def __init__(self, ubicaciones: RepositorioUbicaciones) -> None:
        self._ubicaciones = ubicaciones

    def ejecutar(self, codigo: str) -> Departamento:
        departamento = next(
            (d for d in self._ubicaciones.listar_departamentos() if d.codigo == codigo), None
        )
        if departamento is None:
            raise EntidadNoEncontradaError(f"No existe un departamento con código {codigo}")
        return departamento


class ListarMunicipios:
    def __init__(self, ubicaciones: RepositorioUbicaciones) -> None:
        self._ubicaciones = ubicaciones

    def ejecutar(self, departamento_codigo: str) -> list[Municipio]:
        ObtenerDepartamento(self._ubicaciones).ejecutar(departamento_codigo)
        return self._ubicaciones.listar_municipios(departamento_codigo)


@dataclass(frozen=True)
class DatosDireccion:
    nombre_recibe: str
    telefono: str
    departamento_codigo: str
    municipio_codigo: str
    direccion: str
    detalle: str


class CrearDireccion:
    def __init__(
        self,
        direcciones: RepositorioDirecciones,
        ubicaciones: RepositorioUbicaciones,
        usuarios: RepositorioUsuarios,
    ) -> None:
        self._direcciones = direcciones
        self._ubicaciones = ubicaciones
        self._usuarios = usuarios

    def ejecutar(self, usuario_id: int, datos: DatosDireccion) -> Direccion:
        usuario = self._usuarios.buscar_por_id(usuario_id)
        if usuario is None:
            raise EntidadNoEncontradaError("No existe el usuario de la sesión")
        municipio = self._ubicaciones.buscar_municipio(datos.municipio_codigo)
        if municipio is None or municipio.departamento.codigo != datos.departamento_codigo:
            raise DireccionInvalidaError("El municipio no existe en el departamento indicado")
        partes = [datos.direccion, datos.detalle] if datos.detalle else [datos.direccion]
        return self._direcciones.guardar(
            Direccion(
                usuario=usuario,
                municipio=municipio,
                detalle=SEPARADOR_DETALLE.join(partes),
                telefono_contacto=datos.telefono,
                nombre_recibe=datos.nombre_recibe,
            )
        )


class ListarDireccionesPropias:
    def __init__(self, direcciones: RepositorioDirecciones) -> None:
        self._direcciones = direcciones

    def ejecutar(self, usuario_id: int) -> list[Direccion]:
        return sorted(
            self._direcciones.listar_por_usuario(usuario_id),
            key=lambda direccion: direccion.id or 0,
        )


class ObtenerDireccionPropia:
    def __init__(self, direcciones: RepositorioDirecciones) -> None:
        self._direcciones = direcciones

    def ejecutar(self, usuario_id: int, direccion_id: int) -> Direccion:
        direccion = self._direcciones.buscar_por_id(direccion_id)
        if direccion is None or direccion.usuario.id != usuario_id:
            raise EntidadNoEncontradaError(f"No existe una dirección con id {direccion_id}")
        return direccion
