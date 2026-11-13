import { Component, computed, inject } from '@angular/core';
import { CatalogoService } from '../../../core/catalogo.service';
import { FiltrosService, Orden } from '../../../core/filtros.service';
import { MarcaService } from '../../../core/marca.service';
import { NOMBRE_TIPO } from '../../../core/marcas';
import { CopPipe } from '../../../shared/cop.pipe';
import { Icono } from '../../../shared/icono';
import { TarjetaMoto } from '../../../shared/tarjeta-moto';

@Component({
  selector: 'app-catalogo',
  imports: [TarjetaMoto, Icono, CopPipe],
  template: `
    <section id="catalogo" class="gutter mx-auto max-w-7xl py-14" aria-labelledby="tituloCatalogo">
      <div class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p class="eyebrow eyebrow-marca text-muted">Paso 2</p>
          <h2 id="tituloCatalogo" class="mt-1 font-display text-2xl font-extrabold md:text-3xl">
            Catálogo <span class="text-accenttext">{{ marcaService.marca()?.nombre }}</span>
          </h2>
          <p class="mt-1 text-sm text-muted">
            Licencia A1 para motos de hasta 125 cc. Licencia A2 para cualquier moto.
          </p>
        </div>
        <label class="flex items-center gap-2 text-sm text-muted" for="orden"
          >Ordenar
          <select
            id="orden"
            class="field h-10 rounded-md px-3 text-sm"
            [value]="filtros.orden()"
            (change)="ordenar($event)"
          >
            <option value="precio-asc">Precio: menor a mayor</option>
            <option value="precio-desc">Precio: mayor a menor</option>
            <option value="cc-asc">Cilindraje: menor a mayor</option>
            <option value="cc-desc">Cilindraje: mayor a menor</option>
          </select>
        </label>
      </div>

      @if (filtros.precioMaximo() !== null || filtros.tipo() !== 'todos') {
        <div class="mt-6 flex flex-wrap items-center gap-2 text-sm">
          <span class="text-muted">Mostrando:</span>
          @if (nombreTipo(); as nombre) {
            <span
              class="inline-flex items-center gap-2 rounded-full bg-accentsoft px-3 py-1 font-medium text-accenttext"
              >{{ nombre }}
              <button
                type="button"
                class="grid h-5 w-5 place-items-center rounded-full hover:bg-[color-mix(in_srgb,currentColor_15%,transparent)]"
                aria-label="Quitar filtro por tipo"
                (click)="filtros.tipo.set('todos')"
              >
                <app-icono nombre="x" class="h-3 w-3" /></button
            ></span>
          }
          @if (filtros.precioMaximo() !== null) {
            <span
              class="num inline-flex items-center gap-2 rounded-full bg-accentsoft px-3 py-1 font-medium text-accenttext"
              >Hasta {{ filtros.precioMaximo() | cop }} según tu cuota
              <button
                type="button"
                class="grid h-5 w-5 place-items-center rounded-full hover:bg-[color-mix(in_srgb,currentColor_15%,transparent)]"
                aria-label="Quitar filtro por cuota"
                (click)="filtros.precioMaximo.set(null)"
              >
                <app-icono nombre="x" class="h-3 w-3" /></button
            ></span>
          }
        </div>
      }

      <p class="num mt-5 text-sm text-muted" aria-live="polite">{{ resumen() }}</p>
      <div class="mt-3 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        @for (moto of lista(); track moto.id) {
          <app-tarjeta-moto [moto]="moto" />
        } @empty {
          <div
            class="col-span-full flex flex-col items-start gap-3 rounded-lg border border-dashed border-line p-8"
          >
            <p class="font-display text-lg font-extrabold">
              Ninguna moto coincide con estos filtros.
            </p>
            <p class="text-sm text-muted">
              Quita el filtro por tipo o por cuota, o mira las tres marcas.
            </p>
            <button
              type="button"
              class="cta h-10 rounded-md px-4 text-sm font-bold"
              (click)="filtros.limpiar()"
            >
              Quitar filtros
            </button>
          </div>
        }
      </div>
      <p class="mt-4 text-xs text-muted">
        Precios de referencia de ejemplo. Cuota estimada con cuota fija: 36 meses, 10 % de cuota
        inicial y tasa del 1,79 % mensual vencida. El valor final lo confirma el asesor.
      </p>
    </section>
  `,
})
export class Catalogo {
  protected readonly marcaService = inject(MarcaService);
  protected readonly filtros = inject(FiltrosService);
  private readonly catalogo = inject(CatalogoService);

  private readonly deLaMarca = computed(() => this.catalogo.porMarca(this.marcaService.actual()));

  protected readonly nombreTipo = computed(() => {
    const tipo = this.filtros.tipo();
    return tipo === 'todos' ? '' : NOMBRE_TIPO[tipo];
  });

  protected readonly lista = computed(() =>
    this.filtros.ordenar(this.filtros.aplicar(this.deLaMarca())),
  );

  protected readonly resumen = computed(() => {
    const total = this.lista().length;
    const marca = this.marcaService.marca();
    return `${total} ${total === 1 ? 'moto' : 'motos'} ${marca ? marca.nombre : 'de las tres marcas'}`;
  });

  protected ordenar(evento: Event): void {
    this.filtros.orden.set((evento.target as HTMLSelectElement).value as Orden);
  }
}
