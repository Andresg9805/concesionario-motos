import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { EstadoEnvio, EventoEnvioApi, ItemPedidoApi, PASOS_ENVIO } from './cuenta-api';
import { MarcaResumenApi } from './motos-api';

export interface MotoAdminApi {
  id: number;
  marca: MarcaResumenApi;
  modelo: string;
  anio: number;
  cilindraje_cc: number;
  tipo: string;
  categoria_licencia: string;
  precio_cop: number;
  disponible: boolean;
  imagen_url: string;
  consumo_km_galon: number;
  costo_mantenimiento_km_cop: number;
  descripcion: string;
  stock: number;
}

export interface MotoEntradaApi {
  marca_id: number;
  modelo: string;
  anio: number;
  cilindraje_cc: number;
  tipo: string;
  precio_cop: number;
  stock: number;
  consumo_km_galon: number;
  costo_mantenimiento_km_cop: number;
  descripcion: string;
  imagen_url: string;
}

export interface AccesorioAdminApi {
  id: number;
  sku: string;
  nombre: string;
  categoria: string;
  fabricante: string;
  descripcion: string;
  precio_cop: number;
  stock: number;
  imagen_url: string;
}

export type AccesorioEntradaApi = Omit<AccesorioAdminApi, 'id'>;

export interface TarifaSoatApi {
  cilindraje_min: number;
  cilindraje_max: number;
  valor_anual_cop: number;
}

export interface ParametrosApi {
  precio_galon_cop: number;
  porcentaje_impuesto: number;
  tarifas_soat: TarifaSoatApi[];
  valor_matricula_cop: number;
  valor_tramites_cop: number;
  tasa_mensual: number;
}

export interface EnvioAdminApi {
  id: number;
  numero_guia: string;
  estado: EstadoEnvio;
  eventos: EventoEnvioApi[];
}

export interface PedidoAdminApi {
  id: number;
  cliente_nombre: string;
  cliente_correo: string;
  estado: 'PENDIENTE_PAGO' | 'PAGADO' | 'EXPIRADO';
  estado_pago: string | null;
  subtotal_cop: number;
  costo_envio_cop: number;
  total_cop: number;
  creado_en: string;
  items: ItemPedidoApi[];
  envio: EnvioAdminApi | null;
}

export type GrupoPedidos = 'despachar' | 'pendientes' | 'entregados' | 'todos';

export function siguientePaso(estado: EstadoEnvio): { estado: EstadoEnvio; nombre: string } | null {
  const indice = PASOS_ENVIO.findIndex((paso) => paso.estado === estado);
  return PASOS_ENVIO[indice + 1] ?? null;
}

export function grupoDelPedido(pedido: PedidoAdminApi): Exclude<GrupoPedidos, 'todos'> {
  if (pedido.estado !== 'PAGADO') {
    return 'pendientes';
  }
  return pedido.envio?.estado === 'ENTREGADO' ? 'entregados' : 'despachar';
}

export function licenciaPorCilindraje(cilindraje: number): 'A1' | 'A2' {
  return cilindraje <= 125 ? 'A1' : 'A2';
}

export function detalleDelError(error: unknown, defecto: string): string {
  const detalle = (error as { error?: { detail?: unknown } } | null)?.error?.detail;
  if (typeof detalle === 'string') {
    return detalle;
  }
  if (Array.isArray(detalle) && detalle.length > 0) {
    const primero = detalle[0] as { loc?: unknown[]; msg?: string };
    const campo = Array.isArray(primero.loc) ? String(primero.loc[primero.loc.length - 1]) : '';
    return campo ? `Revisa el campo ${campo}: ${primero.msg ?? 'no es válido'}` : defecto;
  }
  return defecto;
}

@Injectable({ providedIn: 'root' })
export class AdminApiService {
  private readonly api = inject(ApiService);

  marcas(): Observable<MarcaResumenApi[]> {
    return this.api.get<MarcaResumenApi[]>('/marcas');
  }

  motos(): Observable<MotoAdminApi[]> {
    return this.api.get<MotoAdminApi[]>('/admin/motos');
  }

  crearMoto(datos: MotoEntradaApi): Observable<MotoAdminApi> {
    return this.api.post<MotoAdminApi>('/admin/motos', datos);
  }

  actualizarMoto(id: number, datos: MotoEntradaApi): Observable<MotoAdminApi> {
    return this.api.put<MotoAdminApi>(`/admin/motos/${id}`, datos);
  }

  eliminarMoto(id: number): Observable<void> {
    return this.api.delete<void>(`/admin/motos/${id}`);
  }

  accesorios(): Observable<AccesorioAdminApi[]> {
    return this.api.get<AccesorioAdminApi[]>('/accesorios');
  }

  crearAccesorio(datos: AccesorioEntradaApi): Observable<AccesorioAdminApi> {
    return this.api.post<AccesorioAdminApi>('/admin/accesorios', datos);
  }

  actualizarAccesorio(id: number, datos: AccesorioEntradaApi): Observable<AccesorioAdminApi> {
    return this.api.put<AccesorioAdminApi>(`/admin/accesorios/${id}`, datos);
  }

  eliminarAccesorio(id: number): Observable<void> {
    return this.api.delete<void>(`/admin/accesorios/${id}`);
  }

  parametros(): Observable<ParametrosApi> {
    return this.api.get<ParametrosApi>('/parametros-costo');
  }

  guardarParametros(datos: ParametrosApi): Observable<ParametrosApi> {
    return this.api.put<ParametrosApi>('/parametros-costo', datos);
  }

  pedidos(): Observable<PedidoAdminApi[]> {
    return this.api.get<PedidoAdminApi[]>('/admin/pedidos');
  }

  avanzarEnvio(envioId: number, estado: EstadoEnvio, nota: string): Observable<EnvioAdminApi> {
    return this.api.patch<EnvioAdminApi>(`/envios/${envioId}/estado`, { estado, nota });
  }
}
