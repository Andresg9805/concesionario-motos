import { Injectable, computed, effect, inject, signal } from '@angular/core';
import { CatalogoService } from './catalogo.service';
import { Accesorio } from './modelos';

export interface ItemCarrito {
  accesorioId: string;
  cantidad: number;
}

export interface LineaCarrito {
  accesorio: Accesorio;
  cantidad: number;
  subtotal: number;
}

const LLAVE = 'cm-carrito';

function leer(): ItemCarrito[] {
  try {
    const datos = JSON.parse(localStorage.getItem(LLAVE) ?? '[]');
    return Array.isArray(datos)
      ? datos.filter(
          (item): item is ItemCarrito =>
            typeof item?.accesorioId === 'string' && Number.isInteger(item?.cantidad),
        )
      : [];
  } catch {
    return [];
  }
}

@Injectable({ providedIn: 'root' })
export class CarritoService {
  private readonly catalogo = inject(CatalogoService);
  private readonly items = signal<ItemCarrito[]>(leer());

  readonly lineas = computed<LineaCarrito[]>(() =>
    this.items().flatMap((item) => {
      const accesorio = this.catalogo.accesorios().find((a) => a.id === item.accesorioId);
      if (!accesorio) {
        return [];
      }
      const cantidad = Math.min(item.cantidad, accesorio.stock);
      return cantidad > 0 ? [{ accesorio, cantidad, subtotal: cantidad * accesorio.precio }] : [];
    }),
  );

  readonly unidades = computed(() => this.lineas().reduce((total, l) => total + l.cantidad, 0));
  readonly subtotal = computed(() => this.lineas().reduce((total, l) => total + l.subtotal, 0));
  readonly vacio = computed(() => this.lineas().length === 0);

  constructor() {
    effect(() => {
      const items = this.items();
      try {
        localStorage.setItem(LLAVE, JSON.stringify(items));
      } catch {
        return;
      }
    });
  }

  cantidadDe(accesorioId: string): number {
    return this.items().find((item) => item.accesorioId === accesorioId)?.cantidad ?? 0;
  }

  agregar(accesorio: Accesorio, cantidad = 1): boolean {
    const actual = this.cantidadDe(accesorio.id);
    if (actual + cantidad > accesorio.stock) {
      return false;
    }
    this.fijar(accesorio, actual + cantidad);
    return true;
  }

  fijar(accesorio: Accesorio, cantidad: number): void {
    const limite = Math.max(0, Math.min(Math.floor(cantidad), accesorio.stock));
    this.items.update((items) => {
      const otros = items.filter((item) => item.accesorioId !== accesorio.id);
      return limite > 0 ? [...otros, { accesorioId: accesorio.id, cantidad: limite }] : otros;
    });
  }

  quitar(accesorioId: string): void {
    this.items.update((items) => items.filter((item) => item.accesorioId !== accesorioId));
  }

  vaciar(): void {
    this.items.set([]);
  }
}
