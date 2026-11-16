import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { AtencionApi, Contacto } from './atencion-api';

export type EstadoCotizacion =
  'NUEVO' | 'CONTACTADO' | 'TEST_DRIVE' | 'NEGOCIANDO' | 'VENDIDO' | 'DESCARTADO';

export type GrupoCotizacion = 'abiertas' | 'vendidas' | 'descartadas';

export interface AtencionAsesorApi extends AtencionApi {
  id: number;
  cliente: Contacto;
  fecha_programada?: string | null;
}

export const NOMBRE_ESTADO: Record<string, string> = {
  NUEVO: 'Nuevo',
  CONTACTADO: 'Contactado',
  TEST_DRIVE: 'Test drive',
  NEGOCIANDO: 'Negociando',
  VENDIDO: 'Vendido',
  DESCARTADO: 'Descartado',
  PENDIENTE: 'Pendiente',
  PROGRAMADO: 'Programado',
  REALIZADO: 'Realizado',
  CANCELADO: 'Cancelado',
};

export const TRANSICIONES: Record<EstadoCotizacion, readonly EstadoCotizacion[]> = {
  NUEVO: ['CONTACTADO', 'DESCARTADO'],
  CONTACTADO: ['TEST_DRIVE', 'NEGOCIANDO', 'DESCARTADO'],
  TEST_DRIVE: ['NEGOCIANDO', 'DESCARTADO'],
  NEGOCIANDO: ['VENDIDO', 'DESCARTADO'],
  VENDIDO: [],
  DESCARTADO: [],
};

export const ETAPAS: readonly EstadoCotizacion[] = [
  'NUEVO',
  'CONTACTADO',
  'TEST_DRIVE',
  'NEGOCIANDO',
  'VENDIDO',
];

export function siguientesEstados(estado: string): readonly EstadoCotizacion[] {
  return TRANSICIONES[estado as EstadoCotizacion] ?? [];
}

export function grupoDe(estado: string): GrupoCotizacion {
  if (estado === 'VENDIDO') {
    return 'vendidas';
  }
  return estado === 'DESCARTADO' ? 'descartadas' : 'abiertas';
}

export function enlaceWhatsapp(celular: string, mensaje: string): string {
  const numero = celular.replace(/\D/g, '');
  const conPais = numero.length === 10 ? `57${numero}` : numero;
  return `https://wa.me/${conPais}?text=${encodeURIComponent(mensaje)}`;
}

export function mensajeCliente(atencion: AtencionAsesorApi, asesor: string): string {
  const nombre = atencion.cliente.nombre.split(' ')[0];
  const moto = `${atencion.moto.marca.nombre} ${atencion.moto.modelo}`;
  if (atencion.tipo === 'TEST_DRIVE') {
    return `Hola ${nombre}, soy ${asesor} de Candela Motors. Te escribo por el test drive de la ${moto} (código ${atencion.codigo}).`;
  }
  return `Hola ${nombre}, soy ${asesor} de Candela Motors. Te escribo por la cotización de la ${moto} (código ${atencion.codigo}).`;
}

export function fechaLocal(fecha: Date): string {
  const dos = (n: number) => String(n).padStart(2, '0');
  return `${fecha.getFullYear()}-${dos(fecha.getMonth() + 1)}-${dos(fecha.getDate())}T${dos(fecha.getHours())}:${dos(fecha.getMinutes())}`;
}

export function mensajeError(error: unknown, defecto: string): string {
  const detalle = (error as { error?: { detail?: unknown } } | null)?.error?.detail;
  return typeof detalle === 'string' ? detalle : defecto;
}

@Injectable({ providedIn: 'root' })
export class AsesorApiService {
  private readonly api = inject(ApiService);

  atenciones(): Observable<AtencionAsesorApi[]> {
    return this.api.get<AtencionAsesorApi[]>('/asesor/atenciones');
  }

  cambiarEstado(id: number, estado: EstadoCotizacion): Observable<AtencionAsesorApi> {
    return this.api.patch<AtencionAsesorApi>(`/cotizaciones/${id}/estado`, { estado });
  }

  colaTestDrives(): Observable<AtencionAsesorApi[]> {
    return this.api.get<AtencionAsesorApi[]>('/asesor/test-drives');
  }

  programarSiguiente(fecha: string): Observable<AtencionAsesorApi> {
    return this.api.post<AtencionAsesorApi>('/asesor/test-drives/siguiente', { fecha });
  }
}
