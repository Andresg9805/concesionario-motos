from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.domain.atencion import Cliente, Cotizacion, TestDrive, Usuario
from app.domain.catalogo import (
    Busqueda,
    CategoriaLicencia,
    Marca,
    Moto,
    TasaCambio,
    TipoMoto,
)
from app.domain.costo_real import ParametrosCosto
from app.domain.pagos_envios import Envio, Pago, ResultadoPago
from app.domain.tienda import (
    Accesorio,
    CategoriaAccesorio,
    Departamento,
    Direccion,
    Municipio,
    Pedido,
)


@dataclass(frozen=True)
class FiltrosMoto:
    marca_id: int | None = None
    tipo: TipoMoto | None = None
    categoria_licencia: CategoriaLicencia | None = None
    precio_min: int | None = None
    precio_max: int | None = None


class RepositorioMotos(ABC):
    @abstractmethod
    def listar(self, filtros: FiltrosMoto) -> list[Moto]: ...

    @abstractmethod
    def buscar_por_id(self, id: int) -> Moto | None: ...

    @abstractmethod
    def guardar(self, moto: Moto) -> Moto: ...

    @abstractmethod
    def eliminar(self, id: int) -> None: ...


class RepositorioMarcas(ABC):
    @abstractmethod
    def listar(self) -> list[Marca]: ...

    @abstractmethod
    def buscar_por_id(self, id: int) -> Marca | None: ...


class RepositorioParametros(ABC):
    @abstractmethod
    def obtener(self) -> ParametrosCosto: ...

    @abstractmethod
    def guardar(self, parametros: ParametrosCosto) -> ParametrosCosto: ...


class RepositorioBusquedas(ABC):
    @abstractmethod
    def guardar(self, busqueda: Busqueda) -> Busqueda: ...


class RepositorioClientes(ABC):
    @abstractmethod
    def guardar(self, cliente: Cliente) -> Cliente: ...

    @abstractmethod
    def buscar_por_correo(self, correo: str) -> Cliente | None: ...


class RepositorioUsuarios(ABC):
    @abstractmethod
    def guardar(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    def buscar_por_correo(self, correo: str) -> Usuario | None: ...

    @abstractmethod
    def listar_asesores(self, marca_id: int) -> list[Usuario]: ...


class RepositorioCotizaciones(ABC):
    @abstractmethod
    def guardar(self, cotizacion: Cotizacion) -> Cotizacion: ...

    @abstractmethod
    def buscar_por_codigo(self, codigo: str) -> Cotizacion | None: ...

    @abstractmethod
    def listar_por_asesor(self, asesor_id: int) -> list[Cotizacion]: ...

    @abstractmethod
    def listar_por_usuario(self, usuario_id: int) -> list[Cotizacion]: ...

    @abstractmethod
    def contar_abiertas_por_asesor(self, marca_id: int) -> dict[int, int]: ...


class RepositorioTestDrives(ABC):
    @abstractmethod
    def guardar(self, test_drive: TestDrive) -> TestDrive: ...

    @abstractmethod
    def buscar_por_codigo(self, codigo: str) -> TestDrive | None: ...

    @abstractmethod
    def listar_pendientes(self, asesor_id: int) -> list[TestDrive]: ...


class ProveedorTasaCambio(ABC):
    @abstractmethod
    def obtener_trm(self) -> TasaCambio: ...


class RepositorioAccesorios(ABC):
    @abstractmethod
    def listar(
        self, categoria: CategoriaAccesorio | None = None, moto_id: int | None = None
    ) -> list[Accesorio]: ...

    @abstractmethod
    def buscar_por_id(self, id: int) -> Accesorio | None: ...

    @abstractmethod
    def guardar(self, accesorio: Accesorio) -> Accesorio: ...

    @abstractmethod
    def eliminar(self, id: int) -> None: ...


class RepositorioUbicaciones(ABC):
    @abstractmethod
    def listar_departamentos(self) -> list[Departamento]: ...

    @abstractmethod
    def listar_municipios(self, departamento_codigo: str) -> list[Municipio]: ...

    @abstractmethod
    def buscar_municipio(self, codigo: str) -> Municipio | None: ...


class RepositorioDirecciones(ABC):
    @abstractmethod
    def guardar(self, direccion: Direccion) -> Direccion: ...

    @abstractmethod
    def buscar_por_id(self, id: int) -> Direccion | None: ...

    @abstractmethod
    def listar_por_usuario(self, usuario_id: int) -> list[Direccion]: ...


class RepositorioPedidos(ABC):
    @abstractmethod
    def crear_con_reserva(self, pedido: Pedido) -> Pedido: ...

    @abstractmethod
    def buscar_por_id(self, id: int) -> Pedido | None: ...

    @abstractmethod
    def guardar(self, pedido: Pedido) -> Pedido: ...

    @abstractmethod
    def listar_por_usuario(self, usuario_id: int) -> list[Pedido]: ...

    @abstractmethod
    def listar_vencidos(self, ahora: datetime) -> list[Pedido]: ...


class RepositorioPagos(ABC):
    @abstractmethod
    def guardar(self, pago: Pago) -> Pago: ...

    @abstractmethod
    def buscar_por_referencia(self, referencia: str) -> Pago | None: ...

    @abstractmethod
    def registrar_evento(self, pago_id: int, checksum: str) -> bool: ...


class RepositorioEnvios(ABC):
    @abstractmethod
    def guardar(self, envio: Envio) -> Envio: ...

    @abstractmethod
    def buscar_por_pedido(self, pedido_id: int) -> Envio | None: ...

    @abstractmethod
    def listar(self) -> list[Envio]: ...


class PasarelaPago(ABC):
    @abstractmethod
    def datos_para_widget(self, pago: Pago) -> dict[str, Any]: ...

    @abstractmethod
    def leer_evento(self, cuerpo: dict[str, Any]) -> ResultadoPago: ...

    @abstractmethod
    def consultar_transaccion(self, transaccion_id: str) -> ResultadoPago: ...
