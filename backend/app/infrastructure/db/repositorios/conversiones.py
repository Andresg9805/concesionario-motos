from datetime import datetime, timedelta, timezone

from app.domain.atencion import Cliente, Rol, Usuario
from app.domain.catalogo import CILINDRAJE_MAXIMO_A1, CategoriaLicencia, Marca, Moto, TipoMoto
from app.domain.pagos_envios import (
    Envio,
    EstadoEnvio,
    EstadoPago,
    EventoEnvio,
    MetodoPago,
    Pago,
)
from app.domain.tienda import (
    Accesorio,
    CategoriaAccesorio,
    Departamento,
    Direccion,
    EstadoPedido,
    ItemPedido,
    Municipio,
    Pedido,
)
from app.infrastructure.models.accesorio import Accesorio as AccesorioModelo
from app.infrastructure.models.departamento import Departamento as DepartamentoModelo
from app.infrastructure.models.direccion import Direccion as DireccionModelo
from app.infrastructure.models.envio import Envio as EnvioModelo
from app.infrastructure.models.marca import Marca as MarcaModelo
from app.infrastructure.models.moto import Moto as MotoModelo
from app.infrastructure.models.municipio import Municipio as MunicipioModelo
from app.infrastructure.models.pago import Pago as PagoModelo
from app.infrastructure.models.pedido import Pedido as PedidoModelo
from app.infrastructure.models.persona import Persona as PersonaModelo
from app.infrastructure.models.usuario import Usuario as UsuarioModelo

ZONA_COLOMBIA = timezone(timedelta(hours=-5), "COT")


def fecha_a_bd(fecha: datetime) -> datetime:
    if fecha.tzinfo is None:
        return fecha
    return fecha.astimezone(ZONA_COLOMBIA).replace(tzinfo=None)


def fecha_desde_bd(fecha: datetime) -> datetime:
    if fecha.tzinfo is not None:
        return fecha
    return fecha.replace(tzinfo=ZONA_COLOMBIA)


def marca_a_dominio(marca: MarcaModelo) -> Marca:
    return Marca(
        id=marca.id,
        nombre=marca.nombre,
        color_hex=marca.color_hex,
        descripcion=marca.descripcion,
    )


def moto_a_dominio(moto: MotoModelo) -> Moto:
    return Moto(
        id=moto.id,
        marca=marca_a_dominio(moto.marca),
        modelo=moto.modelo,
        anio=moto.anio,
        cilindraje_cc=moto.cilindraje_cc,
        tipo=TipoMoto(moto.tipo.clave),
        precio_cop=moto.precio_cop,
        stock=moto.stock,
        consumo_km_galon=moto.consumo_km_galon,
        costo_mantenimiento_km_cop=moto.costo_mantenimiento_km_cop,
        descripcion=moto.descripcion,
        imagen_url=moto.imagen_url,
    )


def usuario_a_dominio(usuario: UsuarioModelo) -> Usuario:
    marca = None if usuario.asesor is None else marca_a_dominio(usuario.asesor.marca)
    return Usuario(
        id=usuario.id,
        nombre=usuario.persona.nombre,
        correo=usuario.persona.correo,
        telefono=usuario.persona.telefono,
        hash_contrasena=usuario.hash_contrasena,
        rol=Rol(usuario.rol),
        marca_especialidad=marca,
    )


def cliente_a_dominio(persona: PersonaModelo) -> Cliente:
    usuario = None if persona.usuario is None else usuario_a_dominio(persona.usuario)
    return Cliente(
        id=persona.id,
        nombre=persona.nombre,
        correo=persona.correo,
        telefono=persona.telefono,
        usuario=usuario,
    )


def rango_cilindraje(licencia: CategoriaLicencia) -> tuple[int, int | None]:
    if licencia == CategoriaLicencia.A1:
        return 0, CILINDRAJE_MAXIMO_A1
    return CILINDRAJE_MAXIMO_A1 + 1, None


def accesorio_a_dominio(accesorio: AccesorioModelo) -> Accesorio:
    return Accesorio(
        id=accesorio.id,
        sku=accesorio.sku,
        nombre=accesorio.nombre,
        categoria=CategoriaAccesorio(accesorio.categoria.clave),
        fabricante=accesorio.fabricante.nombre,
        descripcion=accesorio.descripcion,
        precio_cop=accesorio.precio_cop,
        stock=accesorio.stock,
        imagen_url=accesorio.imagen_url,
    )


def departamento_a_dominio(departamento: DepartamentoModelo) -> Departamento:
    return Departamento(
        codigo=departamento.codigo,
        nombre=departamento.nombre,
        costo_envio_cop=departamento.costo_envio_cop,
        dias_envio=departamento.dias_envio,
    )


def municipio_a_dominio(municipio: MunicipioModelo) -> Municipio:
    return Municipio(
        codigo=municipio.codigo,
        nombre=municipio.nombre,
        departamento=departamento_a_dominio(municipio.departamento),
    )


def direccion_a_dominio(direccion: DireccionModelo) -> Direccion:
    return Direccion(
        id=direccion.id,
        usuario=usuario_a_dominio(direccion.usuario),
        municipio=municipio_a_dominio(direccion.municipio),
        detalle=direccion.detalle,
        telefono_contacto=direccion.telefono_contacto,
        nombre_recibe=direccion.nombre_recibe,
    )


def pedido_a_dominio(pedido: PedidoModelo) -> Pedido:
    items = [
        ItemPedido(
            accesorio=accesorio_a_dominio(item.accesorio),
            cantidad=item.cantidad,
            precio_unitario_cop=item.precio_unitario_cop,
        )
        for item in sorted(pedido.items, key=lambda item: item.id)
    ]
    return Pedido(
        id=pedido.id,
        usuario=usuario_a_dominio(pedido.usuario),
        direccion=direccion_a_dominio(pedido.direccion),
        items=items,
        estado=EstadoPedido(pedido.estado),
        subtotal_cop=sum(item.subtotal() for item in items),
        costo_envio_cop=pedido.costo_envio_cop,
        creado_en=fecha_desde_bd(pedido.creado_en),
        reservado_hasta=fecha_desde_bd(pedido.reservado_hasta),
    )


def pago_a_dominio(pago: PagoModelo) -> Pago:
    return Pago(
        id=pago.id,
        pedido=pedido_a_dominio(pago.pedido),
        referencia=pago.referencia,
        transaccion_id=pago.transaccion_id,
        metodo=MetodoPago(pago.metodo),
        estado=EstadoPago(pago.estado),
        monto_cop=pago.monto_cop,
    )


def envio_a_dominio(envio: EnvioModelo) -> Envio:
    pedido = pedido_a_dominio(envio.pedido)
    eventos = [
        EventoEnvio(
            estado=EstadoEnvio(evento.estado),
            fecha=fecha_desde_bd(evento.fecha),
            nota=evento.nota,
        )
        for evento in sorted(envio.eventos, key=lambda evento: (evento.fecha, evento.id))
    ]
    return Envio(
        id=envio.id,
        pedido=pedido,
        numero_guia=envio.numero_guia,
        costo_cop=pedido.costo_envio_cop,
        estado=eventos[-1].estado if eventos else EstadoEnvio.PREPARANDO,
        eventos=eventos,
    )
