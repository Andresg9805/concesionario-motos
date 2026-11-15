from app.domain.atencion import Cliente, Rol, Usuario
from app.domain.catalogo import CILINDRAJE_MAXIMO_A1, CategoriaLicencia, Marca, Moto, TipoMoto
from app.infrastructure.models.marca import Marca as MarcaModelo
from app.infrastructure.models.moto import Moto as MotoModelo
from app.infrastructure.models.persona import Persona as PersonaModelo
from app.infrastructure.models.usuario import Usuario as UsuarioModelo


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
