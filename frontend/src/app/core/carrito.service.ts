import { Injectable, computed, effect, inject, signal, untracked } from '@angular/core';
import { CatalogoService } from './catalogo.service';
import { Accesorio } from './modelos';
import { SesionService } from './sesion.service';

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

export function llaveDelCarrito(usuarioId: string | null): string {
  return usuarioId ? `${LLAVE}:${usuarioId}` : LLAVE;
}

function leer(llave: string): ItemCarrito[] {
  try {
    const datos = JSON.parse(localStorage.getItem(llave) ?? '[]');
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

function escribir(llave: string, items: ItemCarrito[]): void {
  try {
    if (items.length > 0) {
      localStorage.setItem(llave, JSON.stringify(items));
    } else {
      localStorage.removeItem(llave);
    }
  } catch {
    return;
  }
}

@Injectable({ providedIn: 'root' })
export class CarritoService {
  private readonly catalogo = inject(CatalogoService);
  private readonly sesion = inject(SesionService);
  private readonly cambios = signal(0);
  private readonly llave = computed(() => llaveDelCarrito(this.sesion.usuario()?.id ?? null));
  private readonly items = computed<ItemCarrito[]>(() => {
    this.cambios();
    return leer(this.llave());
  });

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
      const usuario = this.sesion.usuario();
      if (usuario) {
        untracked(() => this.traerCarritoDeVisitante(llaveDelCarrito(usuario.id)));
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
    const otros = this.items().filter((item) => item.accesorioId !== accesorio.id);
    this.guardar(limite > 0 ? [...otros, { accesorioId: accesorio.id, cantidad: limite }] : otros);
  }

  quitar(accesorioId: string): void {
    this.guardar(this.items().filter((item) => item.accesorioId !== accesorioId));
  }

  vaciar(): void {
    this.guardar([]);
  }

  private guardar(items: ItemCarrito[]): void {
    escribir(this.llave(), items);
    this.cambios.update((n) => n + 1);
  }

  private traerCarritoDeVisitante(llaveUsuario: string): void {
    const visitante = leer(LLAVE);
    if (visitante.length === 0) {
      return;
    }
    const propios = leer(llaveUsuario);
    const nuevos = visitante.filter(
      (item) => !propios.some((propio) => propio.accesorioId === item.accesorioId),
    );
    escribir(llaveUsuario, [...propios, ...nuevos]);
    escribir(LLAVE, []);
    this.cambios.update((n) => n + 1);
  }
}
