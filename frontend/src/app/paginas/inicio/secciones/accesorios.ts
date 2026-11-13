import { Component, computed, inject, signal } from '@angular/core';
import { CarritoService } from '../../../core/carrito.service';
import { CatalogoService } from '../../../core/catalogo.service';
import { Accesorio, CategoriaAccesorio } from '../../../core/modelos';
import { SesionService } from '../../../core/sesion.service';
import { UiService } from '../../../core/ui.service';
import { CopPipe } from '../../../shared/cop.pipe';
import { Icono } from '../../../shared/icono';
import { IlustracionAccesorio } from '../../../shared/ilustracion-accesorio';

type Filtro = 'Todos' | CategoriaAccesorio;

@Component({
  selector: 'app-accesorios',
  imports: [IlustracionAccesorio, Icono, CopPipe],
  template: `
    <section
      id="accesorios"
      class="relative overflow-hidden border-y border-line bg-surface"
      aria-labelledby="tituloAccesorios"
    >
      <div
        class="seigaiha pointer-events-none absolute top-0 -left-10 h-32 w-72 opacity-40"
        aria-hidden="true"
      ></div>
      <div class="gutter relative mx-auto max-w-7xl py-14">
        <div class="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p class="eyebrow eyebrow-marca text-muted">Tienda en línea</p>
            <h2 id="tituloAccesorios" class="mt-1 font-display text-2xl font-extrabold md:text-3xl">
              Accesorios y protección
            </h2>
            <p class="mt-1 max-w-xl text-sm text-muted">
              Pago 100 % virtual y envío con seguimiento. Al pagar, separamos tu stock durante 15
              minutos.
            </p>
          </div>
          <div class="flex flex-wrap gap-2" role="group" aria-label="Categoría de accesorio">
            @for (categoria of categorias; track categoria) {
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
      </div>
    </section>
  `,
})
export class Accesorios {
  private readonly catalogo = inject(CatalogoService);
  private readonly sesion = inject(SesionService);
  private readonly ui = inject(UiService);
  private readonly carrito = inject(CarritoService);

  protected readonly categorias: readonly Filtro[] = [
    'Todos',
    'Cascos',
    'Chaquetas',
    'Rodilleras',
    'Hombreras',
  ];
  protected readonly filtro = signal<Filtro>('Todos');

  protected readonly lista = computed(() =>
    this.catalogo
      .accesorios()
      .filter((a) => this.filtro() === 'Todos' || a.categoria === this.filtro()),
  );

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
