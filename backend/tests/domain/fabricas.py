from datetime import date, datetime

from app.domain.atencion import Cliente, Cotizacion, Rol, TestDrive, Usuario
from app.domain.catalogo import Marca, Moto, PlanCredito, TipoMoto
from app.domain.tienda import (
    Accesorio,
    CategoriaAccesorio,
    Departamento,
    Direccion,
    ItemPedido,
    Municipio,
    Pedido,
)

AHORA = datetime(2026, 11, 9, 10, 0)


def marca(nombre: str = "Kawasaki") -> Marca:
    colores = {"Honda": "#CC0000", "Kawasaki": "#66CC33", "Yamaha": "#0033A0"}
    return Marca(id=1, nombre=nombre, color_hex=colores[nombre])


def moto(cilindraje_cc: int = 399, precio_cop: int = 30_000_000, stock: int = 3) -> Moto:
    return Moto(
        id=1,
        marca=marca(),
        modelo="Ninja 400",
        anio=2026,
        cilindraje_cc=cilindraje_cc,
        tipo=TipoMoto.DEPORTIVA,
        precio_cop=precio_cop,
        stock=stock,
        consumo_km_galon=90.0,
        costo_mantenimiento_km_cop=60,
    )


def asesor(nombre_marca: str = "Kawasaki") -> Usuario:
    return Usuario(
        id=2,
        nombre="Asesor",
        correo="asesor@candela.co",
        telefono="300 123 4567",
        hash_contrasena="hash",
        rol=Rol.ASESOR,
        marca_especialidad=marca(nombre_marca),
    )


def cliente_usuario(correo: str = "ana@correo.com") -> Usuario:
    return Usuario(id=3, nombre="Ana", correo=correo, hash_contrasena="hash", rol=Rol.CLIENTE)


def cliente() -> Cliente:
    return Cliente(nombre="Ana", correo="ana@correo.com", telefono="3001234567")


def plan(precio_cop: int = 30_000_000) -> PlanCredito:
    return PlanCredito(
        precio_cop=precio_cop, cuota_inicial_cop=5_000_000, plazo_meses=36, tasa_mensual=0.02
    )


def cotizacion() -> Cotizacion:
    return Cotizacion(
        codigo_seguimiento="CM-7F3K",
        cliente=cliente(),
        moto=moto(),
        asesor=asesor(),
        fecha=date(2026, 11, 9),
        plan=plan(),
    )


def test_drive() -> TestDrive:
    return TestDrive(
        codigo_seguimiento="CM-A1B2",
        cliente=cliente(),
        moto=moto(),
        asesor=asesor(),
        fecha_solicitud=AHORA,
    )


def accesorio(precio_cop: int = 250_000, stock: int = 5) -> Accesorio:
    return Accesorio(
        id=10,
        sku="CAS-001",
        nombre="Casco integral",
        categoria=CategoriaAccesorio.CASCO,
        precio_cop=precio_cop,
        stock=stock,
    )


def direccion(usuario: Usuario | None = None) -> Direccion:
    cundinamarca = Departamento(
        codigo="25", nombre="Cundinamarca", costo_envio_cop=12_000, dias_envio=2
    )
    chia = Municipio(codigo="25175", nombre="Chía", departamento=cundinamarca)
    return Direccion(
        id=1,
        usuario=usuario or cliente_usuario(),
        municipio=chia,
        detalle="Calle 10 # 5-20",
        telefono_contacto="3001234567",
    )


def pedido() -> Pedido:
    usuario = cliente_usuario()
    items = [ItemPedido.desde_accesorio(accesorio(), 2)]
    return Pedido.crear(usuario, direccion(usuario), items, AHORA)
