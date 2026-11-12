import { Component, computed, inject } from '@angular/core';
import { CatalogoService } from '../../../core/catalogo.service';
import { MarcaService } from '../../../core/marca.service';
import { LISTA_MARCAS } from '../../../core/marcas';
import { ClaveMarca } from '../../../core/modelos';
import { Icono } from '../../../shared/icono';
import { TarjetaMoto } from '../../../shared/tarjeta-moto';

interface OpcionMarca {
  clave: ClaveMarca | null;
  nombre: string;
  kanji: string;
  subtitulo: string;
  color: string;
  cantidad: number;
}

@Component({
  selector: 'app-marcas',
  imports: [TarjetaMoto, Icono],
  template: `
    <section
      id="marcas"
      class="band relative overflow-hidden bg-band text-onband"
      aria-labelledby="tituloMarcas"
    >
      <div class="resplandor pointer-events-none absolute inset-0" aria-hidden="true"></div>
      <div class="gutter relative mx-auto max-w-7xl pt-11 pb-5">
        <div class="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p class="eyebrow eyebrow-marca text-bandmuted">Paso 1</p>
            <h2 id="tituloMarcas" class="mt-1 font-display text-2xl font-extrabold md:text-3xl">
              Elige tu marca
            </h2>
            <p class="mt-1 max-w-xl text-sm text-bandmuted">
              La página adopta los colores de la marca elegida para que identifiques sus modelos de
              un vistazo.
            </p>
          </div>
          <p class="text-sm text-bandmuted" aria-live="polite">{{ estado() }}</p>
        </div>
        <div
          role="radiogroup"
          aria-labelledby="tituloMarcas"
          class="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4"
        >
          @for (opcion of opciones(); track opcion.nombre) {
            <button
              type="button"
              role="radio"
              [attr.aria-checked]="opcion.clave === marcaService.actual()"
              [attr.tabindex]="opcion.clave === marcaService.actual() ? 0 : -1"
              class="brand-card group relative flex min-h-[112px] flex-col justify-between overflow-hidden rounded-lg border border-bandline p-4 text-left hover:border-bandmuted"
              (click)="marcaService.elegir(opcion.clave)"
            >
              <span
                class="pointer-events-none absolute -top-2 -right-1 font-display text-5xl font-extrabold opacity-[.09]"
                aria-hidden="true"
                >{{ opcion.kanji }}</span
              >
              <span class="flex min-w-0 items-center gap-2"
                ><span
                  class="brand-dot shrink-0 h-2.5 w-2.5 rounded-full"
                  [style.background]="opcion.color"
                ></span
                ><span class="truncate text-xs text-bandmuted">{{ opcion.subtitulo }}</span></span
              >
              <span
                class="flex flex-col items-start gap-0.5 lg:flex-row lg:items-end lg:justify-between lg:gap-2"
                ><span
                  class="font-display text-xl leading-tight font-extrabold whitespace-nowrap md:text-2xl"
                  >{{ opcion.nombre }}</span
                ><span class="num shrink-0 text-xs text-bandmuted"
                  >{{ opcion.cantidad }} modelos</span
                ></span
              >
            </button>
          }
        </div>
      </div>

      <div class="gutter relative mx-auto max-w-7xl pt-7 pb-[52px]">
        <div
          class="flex flex-wrap items-baseline justify-between gap-2 border-t border-bandline pt-6"
        >
          <h3 class="font-display text-xl font-extrabold">
            Motos recomendadas del mercado
            <span class="text-bandmuted"
              >· {{ marcaService.marca()?.nombre ?? 'selección multimarca' }}</span
            >
          </h3>
          <a
            href="#catalogo"
            class="inline-flex items-center gap-1 text-sm font-medium text-bandmuted hover:text-onband"
            >Ver catálogo completo <app-icono nombre="arrow-down" class="h-4 w-4"
          /></a>
        </div>
        <div class="mt-5 grid gap-4 md:grid-cols-3">
          @for (moto of recomendadas(); track moto.id; let i = $index) {
            <app-tarjeta-moto [moto]="moto" [banda]="true" [destacada]="i === 0" />
          }
        </div>
      </div>
    </section>
  `,
})
export class Marcas {
  protected readonly marcaService = inject(MarcaService);
  private readonly catalogo = inject(CatalogoService);

  protected readonly opciones = computed<OpcionMarca[]>(() => [
    {
      clave: null,
      nombre: 'Ver todas',
      kanji: '全',
      subtitulo: 'Paleta neutra',
      color: 'var(--band-muted)',
      cantidad: this.catalogo.motos().length,
    },
    ...LISTA_MARCAS.map((marca) => ({
      clave: marca.clave,
      nombre: marca.nombre,
      kanji: marca.kanji,
      subtitulo: marca.origen,
      color: marca.color,
      cantidad: this.catalogo.porMarca(marca.clave).length,
    })),
  ]);

  protected readonly recomendadas = computed(() =>
    this.catalogo.recomendadas(this.marcaService.actual()),
  );

  protected readonly estado = computed(() => {
    const marca = this.marcaService.marca();
    return `Paleta activa: ${marca ? marca.nombre : 'neutra'}`;
  });
}
