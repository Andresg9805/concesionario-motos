import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from './api.service';
import { CategoriaLicencia, ClaveMarca, Moto, TipoMoto } from './modelos';

export type UsoMoto = 'CIUDAD' | 'CARRETERA' | 'TRABAJO';

export const PLAZO_MINIMO = 6;
export const PLAZO_MAXIMO = 72;

export interface MarcaResumenApi {
  id: number;
  nombre: string;
  clave: string;
  color_hex: string;
}

export interface MotoApi {
  id: number;
  marca: MarcaResumenApi;
  modelo: string;
  anio: number;
  cilindraje_cc: number;
  tipo: TipoMoto;
  categoria_licencia: CategoriaLicencia;
  precio_cop: number;
  disponible: boolean;
  imagen_url: string;
}

export interface MotoDetalleApi extends MotoApi {
  consumo_km_galon: number;
  costo_mantenimiento_km_cop: number;
  descripcion: string;
}

export interface ConsultaCostoReal {
  km_mes: number;
  uso: UsoMoto;
  cuota_inicial_cop: number;
  plazo_meses: number;
  ganancia_diaria_cop: number;
  dias_trabajo_mes: number;
}

export interface CostoRealApi {
  moto: MotoApi;
  km_mes: number;
  uso: UsoMoto;
  adquisicion: {
    precio_lista_cop: number;
    matricula_cop: number;
    soat_cop: number;
    impuesto_cop: number;
    tramites_cop: number;
    total_cop: number;
  };
  financiacion: {
    cuota_inicial_cop: number;
    monto_financiado_cop: number;
    plazo_meses: number;
    tasa_mensual: number;
    cuota_mensual_cop: number;
  };
  mensual: {
    cuota_credito_cop: number;
    gasolina_cop: number;
    soat_cop: number;
    mantenimiento_cop: number;
    impuesto_cop: number;
    total_cop: number;
  };
  modo_trabajo: {
    ganancia_mensual_cop: number;
    ganancia_neta_mensual_cop: number;
    meses_para_pagarse: number | null;
  } | null;
}

const CLAVES: Record<string, ClaveMarca> = {
  honda: 'honda',
  kawasaki: 'kawasaki',
  yamaha: 'yamaha',
};

export function claveDeMarca(marca: MarcaResumenApi): ClaveMarca {
  return CLAVES[marca.clave.toLowerCase()] ?? CLAVES[marca.nombre.toLowerCase()] ?? 'honda';
}

export function motoDesdeApi(moto: MotoApi): Moto {
  return {
    id: String(moto.id),
    marca: claveDeMarca(moto.marca),
    modelo: moto.modelo,
    cc: moto.cilindraje_cc,
    tipo: moto.tipo,
    precio: moto.precio_cop,
  };
}

@Injectable({ providedIn: 'root' })
export class MotosApiService {
  private readonly api = inject(ApiService);

  listar(): Observable<Moto[]> {
    return this.api.get<MotoApi[]>('/motos').pipe(map((motos) => motos.map(motoDesdeApi)));
  }

  detalle(id: string): Observable<MotoDetalleApi> {
    return this.api.get<MotoDetalleApi>(`/motos/${encodeURIComponent(id)}`);
  }

  costoReal(id: string, consulta: ConsultaCostoReal): Observable<CostoRealApi> {
    return this.api.get<CostoRealApi>(`/motos/${encodeURIComponent(id)}/costo-real`, {
      ...consulta,
    });
  }
}
