from datetime import date, timedelta

import pytest

from app.domain import excepciones
from app.domain.atencion import Cotizacion, EstadoAtencion, EstadoTestDrive, Rol, Usuario
from app.domain.excepciones import TransicionInvalidaError
from tests.domain import fabricas


def test_asesor_sin_marca_no_es_valido():
    with pytest.raises(ValueError):
        Usuario(nombre="X", correo="x@candela.co", hash_contrasena="h", rol=Rol.ASESOR)


def test_cliente_no_puede_tener_marca_de_especialidad():
    with pytest.raises(ValueError):
        Usuario(
            nombre="X",
            correo="x@correo.com",
            hash_contrasena="h",
            rol=Rol.CLIENTE,
            marca_especialidad=fabricas.marca(),
        )


def test_correo_se_guarda_en_minusculas():
    assert fabricas.cliente_usuario(correo=" ANA@Correo.com ").correo == "ana@correo.com"


def test_roles():
    assert fabricas.asesor().es_asesor()
    assert not fabricas.asesor().es_admin()
    admin = Usuario(nombre="Admin", correo="a@candela.co", hash_contrasena="h", rol=Rol.ADMIN)
    assert admin.es_admin()


def test_enlace_de_whatsapp_con_indicativo_de_colombia():
    assert fabricas.asesor().enlace_whatsapp() == "https://wa.me/573001234567"


def test_cotizacion_empieza_nueva_y_abierta():
    cotizacion = fabricas.cotizacion()
    assert cotizacion.estado == EstadoAtencion.NUEVO
    assert cotizacion.esta_abierta()
    assert cotizacion.cuota_mensual() == fabricas.plan().cuota_mensual()


def test_flujo_completo_hasta_vendido():
    cotizacion = fabricas.cotizacion()
    for estado in (
        EstadoAtencion.CONTACTADO,
        EstadoAtencion.TEST_DRIVE,
        EstadoAtencion.NEGOCIANDO,
        EstadoAtencion.VENDIDO,
    ):
        cotizacion.cambiar_estado(estado)
    assert cotizacion.estado == EstadoAtencion.VENDIDO
    assert not cotizacion.esta_abierta()


def test_se_puede_negociar_sin_test_drive():
    cotizacion = fabricas.cotizacion()
    cotizacion.cambiar_estado(EstadoAtencion.CONTACTADO)
    cotizacion.cambiar_estado(EstadoAtencion.NEGOCIANDO)
    assert cotizacion.estado == EstadoAtencion.NEGOCIANDO


def test_no_se_puede_saltar_de_nuevo_a_vendido():
    with pytest.raises(TransicionInvalidaError):
        fabricas.cotizacion().cambiar_estado(EstadoAtencion.VENDIDO)


def test_descartada_ya_no_cambia():
    cotizacion = fabricas.cotizacion()
    cotizacion.cambiar_estado(EstadoAtencion.DESCARTADO)
    with pytest.raises(TransicionInvalidaError):
        cotizacion.cambiar_estado(EstadoAtencion.CONTACTADO)


@pytest.mark.parametrize("codigo", ["CM-12", "XX-7F3K", "cm-7f3k", "CM-7F3K9"])
def test_codigo_de_seguimiento_con_formato_incorrecto(codigo):
    with pytest.raises(ValueError):
        Cotizacion(
            codigo_seguimiento=codigo,
            cliente=fabricas.cliente(),
            moto=fabricas.moto(),
            asesor=fabricas.asesor(),
            fecha=date(2026, 11, 9),
            plan=fabricas.plan(),
        )


def test_asesor_de_otra_marca_no_puede_atender():
    with pytest.raises(ValueError):
        Cotizacion(
            codigo_seguimiento="CM-7F3K",
            cliente=fabricas.cliente(),
            moto=fabricas.moto(),
            asesor=fabricas.asesor("Honda"),
            fecha=date(2026, 11, 9),
            plan=fabricas.plan(),
        )


def test_plan_con_otro_precio_no_es_valido():
    with pytest.raises(ValueError):
        Cotizacion(
            codigo_seguimiento="CM-7F3K",
            cliente=fabricas.cliente(),
            moto=fabricas.moto(),
            asesor=fabricas.asesor(),
            fecha=date(2026, 11, 9),
            plan=fabricas.plan(precio_cop=20_000_000),
        )


def test_test_drive_se_programa_y_se_realiza():
    test_drive = fabricas.test_drive()
    fecha = fabricas.AHORA + timedelta(days=2)
    test_drive.programar(fecha)
    assert test_drive.estado == EstadoTestDrive.PROGRAMADO
    assert test_drive.fecha_programada == fecha
    test_drive.marcar_realizado()
    assert test_drive.estado == EstadoTestDrive.REALIZADO


def test_test_drive_no_se_programa_en_el_pasado():
    with pytest.raises(excepciones.TestDriveInvalidoError):
        fabricas.test_drive().programar(fabricas.AHORA - timedelta(hours=1))


def test_no_se_realiza_un_test_drive_sin_programar():
    with pytest.raises(TransicionInvalidaError):
        fabricas.test_drive().marcar_realizado()


def test_test_drive_cancelado_no_se_reprograma():
    test_drive = fabricas.test_drive()
    test_drive.cancelar()
    with pytest.raises(TransicionInvalidaError):
        test_drive.programar(fabricas.AHORA + timedelta(days=1))
