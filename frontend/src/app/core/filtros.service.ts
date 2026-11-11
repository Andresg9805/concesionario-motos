import { Injectable, signal } from '@angular/core';
import { Moto } from './modelos';

export interface Segmento {
  id: 'todas' | 'a1' | 'a2';
  texto: string;
  cumple: (moto: Moto) => boolean;
}

export interface Rango {
  id: string;
  texto: string;
  minimo: number;
  maximo: number;
}

export type Orden = 'precio-asc' | 'precio-desc' | 'cc-asc' | 'cc-desc';

export const SEGMENTOS: readonly Segmento[] = [
  { id: 'todas', texto: 'Todas', cumple: () => true },
  { id: 'a1', texto: 'A1 · hasta 125 cc', cumple: (moto) => moto.cc <= 125 },
  { id: 'a2', texto: 'A2 · más de 125 cc', cumple: (moto) => moto.cc > 125 },
];

export const RANGOS: readonly Rango[] = [
  { id: 'todos', texto: 'Todos', minimo: 0, maximo: Infinity },
  { id: 'r1', texto: 'Hasta $10 M', minimo: 0, maximo: 10_000_000 },
  { id: 'r2', texto: '$10 M – $20 M', minimo: 10_000_000, maximo: 20_000_000 },
  { id: 'r3', texto: '$20 M – $40 M', minimo: 20_000_000, maximo: 40_000_000 },
  { id: 'r4', texto: 'Más de $40 M', minimo: 40_000_000, maximo: Infinity },
];

@Injectable({ providedIn: 'root' })
export class FiltrosService {
  readonly segmento = signal<Segmento['id']>('todas');
  readonly rango = signal('todos');
  readonly orden = signal<Orden>('precio-asc');
  readonly precioMaximo = signal<number | null>(null);

  aplicar(motos: readonly Moto[], ignorarSegmento = false): Moto[] {
    const segmento = SEGMENTOS.find((s) => s.id === this.segmento()) ?? SEGMENTOS[0];
    const rango = RANGOS.find((r) => r.id === this.rango()) ?? RANGOS[0];
    const maximo = this.precioMaximo();
    return motos
      .filter((moto) => ignorarSegmento || segmento.cumple(moto))
      .filter((moto) => moto.precio >= rango.minimo && moto.precio < rango.maximo)
      .filter((moto) => maximo === null || moto.precio <= maximo);
  }

  ordenar(motos: Moto[]): Moto[] {
    const [campo, direccion] = this.orden().split('-') as ['precio' | 'cc', 'asc' | 'desc'];
    const signo = direccion === 'asc' ? 1 : -1;
    return [...motos].sort((a, b) => signo * (a[campo] - b[campo]));
  }

  limpiar(): void {
    this.segmento.set('todas');
    this.rango.set('todos');
    this.precioMaximo.set(null);
  }
}
