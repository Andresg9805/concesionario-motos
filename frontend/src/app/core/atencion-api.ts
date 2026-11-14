import { HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, catchError, map, of, throwError } from 'rxjs';
import { ApiService } from './api.service';
import { AtencionService } from './atencion.service';
import { Atencion, Moto, TipoAtencion } from './modelos';
import { MarcaResumenApi, claveDeMarca } from './motos-api';

export interface Contacto {
  nombre: string;
  correo: string;
  celular: string;
}

export interface Credito {
  cuota_inicial_cop: number;
  plazo_meses: number;
}

export interface AtencionApi {
  codigo: string;
  tipo: 'COTIZACION' | 'TEST_DRIVE';
  estado: string;
  creada_en: string;
  moto: { id: number; modelo: string; marca: MarcaResumenApi };
  asesor: { nombre: string; whatsapp: string };
  cuota_mensual_cop: number | null;
}

export function atencionDesdeApi(dato: AtencionApi): Atencion {
  return {
    codigo: dato.codigo,
    tipo: dato.tipo === 'TEST_DRIVE' ? 'testdrive' : 'cotizacion',
    estado: dato.estado,
    asesor: { nombre: dato.asesor.nombre, whatsapp: dato.asesor.whatsapp, abiertas: 0 },
    marca: claveDeMarca(dato.moto.marca),
    moto: dato.moto.modelo,
  };
}

function sinServidor(error: unknown): boolean {
  return error instanceof HttpErrorResponse && (error.status === 0 || error.status === 404);
}

@Injectable({ providedIn: 'root' })
export class AtencionApiService {
  private readonly api = inject(ApiService);
  private readonly local = inject(AtencionService);

  solicitar(
    moto: Moto,
    tipo: TipoAtencion,
    contacto: Contacto,
    credito: Credito | null,
  ): Observable<Atencion> {
    if (!/^\d+$/.test(moto.id)) {
      return of(this.local.registrar(moto, tipo));
    }
    const cuerpo = {
      moto_id: Number(moto.id),
      nombre: contacto.nombre,
      correo: contacto.correo,
      celular: contacto.celular,
      acepta_contacto: true,
      ...(tipo === 'cotizacion' && credito ? credito : {}),
    };
    const ruta = tipo === 'testdrive' ? '/test-drives' : '/cotizaciones';
    return this.api.post<AtencionApi>(ruta, cuerpo).pipe(
      map(atencionDesdeApi),
      catchError((error) =>
        sinServidor(error) ? of(this.local.registrar(moto, tipo)) : throwError(() => error),
      ),
    );
  }

  buscar(codigo: string): Observable<Atencion | undefined> {
    const limpio = codigo.trim().toUpperCase();
    return this.api.get<AtencionApi>(`/seguimiento/${encodeURIComponent(limpio)}`).pipe(
      map(atencionDesdeApi),
      catchError(() => of(this.local.consultar(limpio))),
    );
  }
}
