import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { AtencionApi } from './atencion-api';

export type EstadoEnvio = 'PREPARANDO' | 'ENVIADO' | 'EN_CAMINO' | 'ENTREGADO';

export interface PedidoResumenApi {
  pedido_id: number;
  estado_pago: string;
  estado_pedido: 'PENDIENTE_PAGO' | 'PAGADO' | 'EXPIRADO';
  total_cop: number;
  numero_guia: string | null;
  reservado_hasta: string | null;
  subtotal_cop: number;
  costo_envio_cop: number;
  creado_en: string;
}

export interface ItemPedidoApi {
  accesorio_id: number;
  nombre: string;
  cantidad: number;
  precio_unitario_cop: number;
  subtotal_cop: number;
}

export interface EventoEnvioApi {
  estado: EstadoEnvio;
  fecha: string;
  nota: string;
}

export interface PedidoDetalleApi extends PedidoResumenApi {
  items: ItemPedidoApi[];
  estado_envio: EstadoEnvio | null;
  eventos: EventoEnvioApi[];
}

export interface DireccionApi {
  id: number;
  nombre_recibe: string;
  telefono: string;
  departamento_codigo: string;
  municipio_codigo: string;
  municipio_nombre: string;
  direccion: string;
  detalle: string;
}

export const PASOS_ENVIO: readonly { estado: EstadoEnvio; nombre: string }[] = [
  { estado: 'PREPARANDO', nombre: 'Preparando' },
  { estado: 'ENVIADO', nombre: 'Enviado' },
  { estado: 'EN_CAMINO', nombre: 'En camino' },
  { estado: 'ENTREGADO', nombre: 'Entregado' },
];

export const NOMBRE_ESTADO_PEDIDO: Record<string, string> = {
  PENDIENTE_PAGO: 'Pendiente de pago',
  PAGADO: 'Pagado',
  EXPIRADO: 'Reserva vencida',
};

export const NOMBRE_ESTADO_COTIZACION: Record<string, string> = {
  NUEVO: 'Recibida',
  CONTACTADO: 'El asesor te contactó',
  TEST_DRIVE: 'Test drive',
  NEGOCIANDO: 'En negociación',
  VENDIDO: 'Moto entregada',
  DESCARTADO: 'Cerrada',
};

export function estadoDelPedido(pedido: PedidoResumenApi): string {
  return NOMBRE_ESTADO_PEDIDO[pedido.estado_pedido] ?? pedido.estado_pedido;
}

export function pasoActual(estado: EstadoEnvio | null): number {
  return estado ? PASOS_ENVIO.findIndex((paso) => paso.estado === estado) : -1;
}

export function fechaDelPaso(eventos: EventoEnvioApi[], estado: EstadoEnvio): string | null {
  return eventos.find((evento) => evento.estado === estado)?.fecha ?? null;
}

@Injectable({ providedIn: 'root' })
export class CuentaApiService {
  private readonly api = inject(ApiService);

  misPedidos(): Observable<PedidoResumenApi[]> {
    return this.api.get<PedidoResumenApi[]>('/mis-pedidos');
  }

  miPedido(id: number): Observable<PedidoDetalleApi> {
    return this.api.get<PedidoDetalleApi>(`/mis-pedidos/${id}`);
  }

  misCotizaciones(): Observable<AtencionApi[]> {
    return this.api.get<AtencionApi[]>('/mis-cotizaciones');
  }

  misDirecciones(): Observable<DireccionApi[]> {
    return this.api.get<DireccionApi[]>('/mis-direcciones');
  }
}
