import { Injectable, inject } from '@angular/core';
import { Observable, catchError, map, of, switchMap } from 'rxjs';
import { ApiService } from './api.service';

export interface Departamento {
  codigo: string;
  nombre: string;
  costo_envio_cop: number;
  dias_envio: number;
}

export interface Municipio {
  codigo: string;
  nombre: string;
}

export interface DatosDireccion {
  nombre_recibe: string;
  telefono: string;
  departamento_codigo: string;
  municipio_codigo: string | null;
  municipio_nombre: string;
  direccion: string;
  detalle: string;
}

export interface DatosWompi {
  llave_publica: string;
  referencia: string;
  monto_centavos: number;
  moneda: string;
  firma_integridad: string;
}

export interface PedidoCreado {
  pedido_id: number;
  total_cop: number;
  reservado_hasta: string;
  wompi: DatosWompi;
}

export type EstadoPago = 'APROBADO' | 'RECHAZADO' | 'PENDIENTE' | 'ERROR';

export interface ResultadoPago {
  pedido_id: number;
  estado_pago: EstadoPago;
  estado_pedido: 'PENDIENTE_PAGO' | 'PAGADO' | 'EXPIRADO';
  total_cop: number;
  numero_guia: string | null;
  reservado_hasta: string | null;
}

function departamento(codigo: string, nombre: string, costo: number, dias: number): Departamento {
  return { codigo, nombre, costo_envio_cop: costo, dias_envio: dias };
}

export const DEPARTAMENTOS_RESPALDO: readonly Departamento[] = [
  departamento('91', 'Amazonas', 29000, 7),
  departamento('05', 'Antioquia', 15000, 3),
  departamento('81', 'Arauca', 29000, 6),
  departamento('08', 'Atlántico', 19000, 4),
  departamento('11', 'Bogotá D.C.', 9000, 1),
  departamento('13', 'Bolívar', 19000, 4),
  departamento('15', 'Boyacá', 15000, 3),
  departamento('17', 'Caldas', 15000, 3),
  departamento('18', 'Caquetá', 29000, 6),
  departamento('85', 'Casanare', 19000, 4),
  departamento('19', 'Cauca', 19000, 4),
  departamento('20', 'Cesar', 19000, 4),
  departamento('27', 'Chocó', 29000, 7),
  departamento('23', 'Córdoba', 19000, 4),
  departamento('25', 'Cundinamarca', 12000, 2),
  departamento('94', 'Guainía', 29000, 8),
  departamento('95', 'Guaviare', 29000, 7),
  departamento('41', 'Huila', 15000, 3),
  departamento('44', 'La Guajira', 19000, 5),
  departamento('47', 'Magdalena', 19000, 4),
  departamento('50', 'Meta', 15000, 3),
  departamento('52', 'Nariño', 19000, 5),
  departamento('54', 'Norte de Santander', 19000, 4),
  departamento('86', 'Putumayo', 29000, 6),
  departamento('63', 'Quindío', 15000, 3),
  departamento('66', 'Risaralda', 15000, 3),
  departamento('88', 'San Andrés y Providencia', 29000, 8),
  departamento('68', 'Santander', 15000, 3),
  departamento('70', 'Sucre', 19000, 4),
  departamento('73', 'Tolima', 15000, 3),
  departamento('76', 'Valle del Cauca', 15000, 3),
  departamento('97', 'Vaupés', 29000, 8),
  departamento('99', 'Vichada', 29000, 8),
];

@Injectable({ providedIn: 'root' })
export class TiendaApiService {
  private readonly api = inject(ApiService);

  departamentos(): Observable<{ lista: Departamento[]; respaldo: boolean }> {
    return this.api.get<Departamento[]>('/departamentos').pipe(
      map((lista) =>
        lista.length
          ? { lista, respaldo: false }
          : { lista: [...DEPARTAMENTOS_RESPALDO], respaldo: true },
      ),
      catchError(() => of({ lista: [...DEPARTAMENTOS_RESPALDO], respaldo: true })),
    );
  }

  municipios(codigo: string): Observable<Municipio[] | null> {
    return this.api
      .get<Municipio[]>(`/departamentos/${encodeURIComponent(codigo)}/municipios`)
      .pipe(catchError(() => of(null)));
  }

  crearPedido(
    direccion: DatosDireccion,
    items: { accesorio_id: string; cantidad: number }[],
  ): Observable<PedidoCreado> {
    return this.api
      .post<{ id: number }>('/mis-direcciones', direccion)
      .pipe(
        switchMap((guardada) =>
          this.api.post<PedidoCreado>('/pedidos', { direccion_id: guardada.id, items }),
        ),
      );
  }

  verificarPago(pedidoId: string, transaccionId: string | null): Observable<ResultadoPago> {
    return this.api.post<ResultadoPago>(
      `/mis-pedidos/${encodeURIComponent(pedidoId)}/verificar-pago`,
      { transaccion_id: transaccionId },
    );
  }
}
