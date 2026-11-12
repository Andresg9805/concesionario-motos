from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.catalogo import CategoriaLicencia, Marca, Moto, TipoMoto, UsoMoto

PLAZO_MINIMO_MESES = 6
PLAZO_MAXIMO_MESES = 72
PATRON_SESION = r"^[A-Za-z0-9-]{8,64}$"


class EntradaConsulta(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FiltrosMotoEntrada(EntradaConsulta):
    marca_id: int | None = Field(default=None, ge=1)
    tipo: TipoMoto | None = None
    licencia: CategoriaLicencia | None = None
    cilindraje_min: int | None = Field(default=None, ge=1)
    cilindraje_max: int | None = Field(default=None, ge=1)
    precio_min: int | None = Field(default=None, ge=0)
    precio_max: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validar_rangos(self) -> "FiltrosMotoEntrada":
        if (
            self.cilindraje_min is not None
            and self.cilindraje_max is not None
            and self.cilindraje_min > self.cilindraje_max
        ):
            raise ValueError("cilindraje_min no puede ser mayor que cilindraje_max")
        if (
            self.precio_min is not None
            and self.precio_max is not None
            and self.precio_min > self.precio_max
        ):
            raise ValueError("precio_min no puede ser mayor que precio_max")
        return self


class PorCuotaEntrada(EntradaConsulta):
    cuota_maxima_cop: int = Field(ge=50_000, le=50_000_000, examples=[350_000])
    cuota_inicial_cop: int = Field(default=0, ge=0, le=500_000_000, examples=[1_000_000])
    plazo_meses: int = Field(
        default=36, ge=PLAZO_MINIMO_MESES, le=PLAZO_MAXIMO_MESES, examples=[36]
    )
    licencia: CategoriaLicencia = CategoriaLicencia.A2
    marca_id: int | None = Field(default=None, ge=1)
    uso: UsoMoto = UsoMoto.CIUDAD


class CostoRealEntrada(EntradaConsulta):
    km_mes: int = Field(default=800, ge=0, le=20_000)
    uso: UsoMoto = UsoMoto.CIUDAD
    cuota_inicial_cop: int = Field(default=0, ge=0)
    plazo_meses: int = Field(default=36, ge=PLAZO_MINIMO_MESES, le=PLAZO_MAXIMO_MESES)
    ganancia_diaria_cop: int = Field(default=0, ge=0, le=5_000_000)
    dias_trabajo_mes: int = Field(default=0, ge=0, le=31)

    @model_validator(mode="after")
    def validar_modo_trabajo(self) -> "CostoRealEntrada":
        if (self.ganancia_diaria_cop > 0) != (self.dias_trabajo_mes > 0):
            raise ValueError(
                "Para el modo trabajo envía ganancia_diaria_cop y dias_trabajo_mes juntos"
            )
        return self


class MarcaSalida(BaseModel):
    id: int
    nombre: str
    clave: str
    color_hex: str
    descripcion: str

    @classmethod
    def desde_dominio(cls, marca: Marca) -> "MarcaSalida":
        return cls(
            id=marca.id or 0,
            nombre=marca.nombre,
            clave=marca.nombre.lower(),
            color_hex=marca.color_hex,
            descripcion=marca.descripcion,
        )


class MarcaResumenSalida(BaseModel):
    id: int
    nombre: str
    clave: str
    color_hex: str

    @classmethod
    def desde_dominio(cls, marca: Marca) -> "MarcaResumenSalida":
        return cls(
            id=marca.id or 0,
            nombre=marca.nombre,
            clave=marca.nombre.lower(),
            color_hex=marca.color_hex,
        )


class MotoResumenSalida(BaseModel):
    id: int
    marca: MarcaResumenSalida
    modelo: str
    anio: int
    cilindraje_cc: int
    tipo: TipoMoto
    categoria_licencia: CategoriaLicencia
    precio_cop: int
    disponible: bool
    imagen_url: str

    @classmethod
    def desde_dominio(cls, moto: Moto) -> "MotoResumenSalida":
        return cls(**_campos_resumen(moto))


class MotoDetalleSalida(MotoResumenSalida):
    consumo_km_galon: float
    costo_mantenimiento_km_cop: int
    descripcion: str

    @classmethod
    def desde_dominio(cls, moto: Moto) -> "MotoDetalleSalida":
        return cls(
            **_campos_resumen(moto),
            consumo_km_galon=moto.consumo_km_galon,
            costo_mantenimiento_km_cop=moto.costo_mantenimiento_km_cop,
            descripcion=moto.descripcion,
        )


def _campos_resumen(moto: Moto) -> dict[str, object]:
    return {
        "id": moto.id or 0,
        "marca": MarcaResumenSalida.desde_dominio(moto.marca),
        "modelo": moto.modelo,
        "anio": moto.anio,
        "cilindraje_cc": moto.cilindraje_cc,
        "tipo": moto.tipo,
        "categoria_licencia": moto.categoria_licencia
        or Moto.categoria_por_cilindraje(moto.cilindraje_cc),
        "precio_cop": moto.precio_cop,
        "disponible": moto.esta_disponible(),
        "imagen_url": moto.imagen_url,
    }


class MotoFinanciableSalida(BaseModel):
    moto: MotoResumenSalida
    cuota_inicial_cop: int
    monto_financiado_cop: int
    cuota_mensual_cop: int


class PorCuotaSalida(BaseModel):
    busqueda_id: int
    sesion_id: str
    simulaciones_en_sesion: int
    cuota_maxima_cop: int
    cuota_inicial_cop: int
    plazo_meses: int
    tasa_mensual: float
    licencia: CategoriaLicencia
    precio_maximo_cop: int
    cantidad_resultados: int
    motos: list[MotoFinanciableSalida]


class CostoAdquisicionSalida(BaseModel):
    precio_lista_cop: int
    matricula_cop: int
    soat_cop: int
    impuesto_cop: int
    tramites_cop: int
    total_cop: int


class FinanciacionSalida(BaseModel):
    cuota_inicial_cop: int
    monto_financiado_cop: int
    plazo_meses: int
    tasa_mensual: float
    cuota_mensual_cop: int


class CostoMensualSalida(BaseModel):
    cuota_credito_cop: int
    gasolina_cop: int
    soat_cop: int
    mantenimiento_cop: int
    impuesto_cop: int
    total_cop: int


class ModoTrabajoSalida(BaseModel):
    ganancia_mensual_cop: int
    ganancia_neta_mensual_cop: int
    meses_para_pagarse: int | None


class CostoRealSalida(BaseModel):
    moto: MotoResumenSalida
    km_mes: int
    uso: UsoMoto
    adquisicion: CostoAdquisicionSalida
    financiacion: FinanciacionSalida
    mensual: CostoMensualSalida
    modo_trabajo: ModoTrabajoSalida | None
