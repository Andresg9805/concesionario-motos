import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ORDEN_CATEGORIAS } from '../../core/accesorios-api';
import { CarritoService } from '../../core/carrito.service';
import { CatalogoService } from '../../core/catalogo.service';
import { Accesorio, CategoriaAccesorio } from '../../core/modelos';
import { SesionService } from '../../core/sesion.service';
import { UiService } from '../../core/ui.service';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';
import { IlustracionAccesorio } from '../../shared/ilustracion-accesorio';

type Filtro = 'Todos' | CategoriaAccesorio;

@Component({
  selector: 'app-tienda',
  imports: [IlustracionAccesorio, Icono, CopPipe, RouterLink],
  template: `
    <section
      class="relative overflow-hidden border-b border-line bg-surface"
      aria-labelledby="tituloTienda"
    >
      <div
        class="seigaiha pointer-events-none absolute top-0 -right-10 h-40 w-96 opacity-40"
        aria-hidden="true"
      ></div>
      <div
        class="gutter relative mx-auto flex max-w-7xl flex-wrap items-end justify-between gap-6 py-12"
      >
        <div class="max-w-2xl">
          <p class="eyebrow text-muted">Tienda Candela</p>
          <h1 id="tituloTienda" class="mt-1 font-display text-3xl font-extrabold md:text-4xl">
            Equipo para el motociclista
          </h1>
          <p class="mt-2 text-sm text-muted">
            Cascos, chaquetas, guantes y protección para rodar seguro. Compras en línea, pagas con
            Wompi y te lo enviamos a cualquier parte de Colombia.
          </p>
          <ul class="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm">
            <li class="flex items-center gap-2">
              <app-icono nombre="wallet" class="h-4 w-4 text-muted" /> Pago 100 % en línea
            </li>
            <li class="flex items-center gap-2">
              <app-icono nombre="map-pin" class="h-4 w-4 text-muted" /> Envío con seguimiento
            </li>
            <li class="flex items-center gap-2">
              <app-icono nombre="clock" class="h-4 w-4 text-muted" /> Stock separado 15 min al pagar
            </li>
          </ul>
        </div>
        <a
          routerLink="/carrito"
          class="cta inline-flex h-11 items-center gap-2 rounded-md px-5 text-sm font-bold"
        >
          <app-icono nombre="shopping-bag" class="h-4 w-4" /> Ver carrito
          @if (carrito.unidades() > 0) {
            <span
              class="num rounded bg-[color-mix(in_srgb,currentColor_18%,transparent)] px-1.5 text-xs"
              >{{ carrito.unidades() }}</span
            >
          }
        </a>
      </div>
    </section>

    <section id="accesorios" class="gutter mx-auto max-w-7xl py-10" aria-label="Productos">
      <div class="flex flex-wrap gap-2" role="group" aria-label="Categoría">
        @for (categoria of categorias(); track categoria) {
          <button
            type="button"
            class="chip h-9 rounded-full border border-line px-3 text-sm font-medium hover:border-muted"
            [attr.aria-pressed]="filtro() === categoria"
            (click)="filtro.set(categoria)"
          >
            {{ categoria }}
          </button>
        }
      </div>
      <div class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        @for (accesorio of lista(); track accesorio.id) {
          <article class="flex flex-col overflow-hidden rounded-lg border border-line bg-bg">
            <div
              class="relative aspect-[4/3] max-w-full bg-surface2 p-8"
              style="color: color-mix(in srgb, var(--fg) 88%, var(--bg))"
            >
              <app-ilustracion-accesorio [tipo]="accesorio.ilustracion" />
              <span
                class="absolute top-3 left-3 rounded bg-surface px-2 py-0.5 text-[11px] font-bold text-muted"
                >{{ accesorio.categoria }}</span
              >
              <span
                class="num absolute top-3 right-3 rounded bg-surface px-2 py-0.5 text-[11px] font-bold"
                [class]="accesorio.stock <= 3 ? 'text-danger' : 'text-muted'"
                >{{ disponibilidad(accesorio) }}</span
              >
            </div>
            <div class="flex flex-1 flex-col gap-2 p-4">
              <h3 class="font-display text-base leading-snug font-extrabold">
                {{ accesorio.nombre }}
              </h3>
              <p class="text-sm text-muted">{{ accesorio.descripcion }}</p>
              <div class="mt-auto flex items-center justify-between gap-3 pt-2">
                <span class="num font-mono text-[15px] font-semibold">{{
                  accesorio.precio | cop
                }}</span>
              </div>
              <button
                type="button"
                class="matte-btn inline-flex h-10 items-center justify-center gap-2 rounded-md text-sm font-bold disabled:cursor-not-allowed disabled:opacity-50"
                [disabled]="accesorio.stock === 0"
                (click)="comprar(accesorio)"
              >
                <app-icono nombre="shopping-bag" class="h-4 w-4" />{{
                  accesorio.stock === 0 ? 'Sin stock' : 'Agregar al carrito'
                }}
              </button>
            </div>
          </article>
        }
      </div>
    </section>
  `,
})
export class Tienda {
  private readonly catalogo = inject(CatalogoService);
  private readonly sesion = inject(SesionService);
  private readonly ui = inject(UiService);
  protected readonly carrito = inject(CarritoService);

  protected readonly categorias = computed<Filtro[]>(() => {
    const presentes = new Set(this.catalogo.accesorios().map((a) => a.categoria));
    const conocidas = ORDEN_CATEGORIAS.filter((c) => presentes.has(c));
    const nuevas = [...presentes].filter((c) => !ORDEN_CATEGORIAS.includes(c));
    return ['Todos', ...conocidas, ...nuevas];
  });
  protected readonly filtro = signal<Filtro>('Todos');

  protected readonly lista = computed(() =>
    this.catalogo
      .accesorios()
      .filter((a) => this.filtro() === 'Todos' || a.categoria === this.filtro()),
  );

  constructor() {
    this.catalogo.cargarAccesorios();
  }

  protected disponibilidad(accesorio: Accesorio): string {
    if (accesorio.stock === 0) {
      return 'Agotado';
    }
    return accesorio.stock <= 3 ? `Quedan ${accesorio.stock}` : `${accesorio.stock} disponibles`;
  }

  protected comprar(accesorio: Accesorio): void {
    if (this.sesion.rol() === 'ASESOR' || this.sesion.rol() === 'ADMIN') {
      this.ui.avisar('Solo las cuentas de cliente pueden comprar accesorios.', 'error');
      return;
    }
    if (this.carrito.agregar(accesorio)) {
      this.ui.avisar(`${accesorio.nombre} quedó en el carrito.`, 'ok');
    } else {
      this.ui.avisar(`No hay más unidades de ${accesorio.nombre}.`, 'error');
    }
  }
}
