import { Injectable, signal } from '@angular/core';
import { Moto, TipoAtencion } from './modelos';

export type TipoAviso = 'info' | 'ok' | 'error';

export interface Aviso {
  id: number;
  mensaje: string;
  tipo: TipoAviso;
}

export interface SolicitudCotizacion {
  moto: Moto;
  tipo: TipoAtencion;
}

@Injectable({ providedIn: 'root' })
export class UiService {
  private siguienteId = 1;

  readonly cotizacion = signal<SolicitudCotizacion | null>(null);
  readonly accesoAbierto = signal(false);
  readonly avisos = signal<Aviso[]>([]);
  readonly codigoBuscado = signal<string | null>(null);

  abrirCotizacion(moto: Moto, tipo: TipoAtencion = 'cotizacion'): void {
    this.cotizacion.set({ moto, tipo });
  }

  cerrarCotizacion(): void {
    this.cotizacion.set(null);
  }

  avisar(mensaje: string, tipo: TipoAviso = 'info'): void {
    const aviso = { id: this.siguienteId++, mensaje, tipo };
    this.avisos.update((lista) => [...lista, aviso]);
    setTimeout(() => this.quitarAviso(aviso.id), 5200);
  }

  quitarAviso(id: number): void {
    this.avisos.update((lista) => lista.filter((aviso) => aviso.id !== id));
  }
}
