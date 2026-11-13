import { Component, computed, inject } from '@angular/core';
import { CatalogoService } from '../../../core/catalogo.service';
import { MarcaService } from '../../../core/marca.service';
import { LISTA_MARCAS, NOMBRE_TIPO, ORDEN_TIPOS } from '../../../core/marcas';
import { ClaveMarca, TipoMoto } from '../../../core/modelos';

const CARPETA_TIPO: Record<TipoMoto, string> = {
  NAKED: 'naked',
  DOBLE_PROPOSITO: 'doble-proposito',
  TRAIL: 'trail',
  DEPORTIVA: 'deportiva',
};

interface ImagenTipo {
  src: string;
  alt: string;
}

interface TarjetaTipo {
  clave: TipoMoto;
  nombre: string;
  imagenes: ImagenTipo[];
}

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
  styles: `
    .rotar {
      opacity: 0;
      animation: rotar 12s infinite;
    }
    .rotar:first-child {
      opacity: 1;
    }
    @keyframes rotar {
      0%,
      30% {
        opacity: 1;
      }
      36%,
      94% {
        opacity: 0;
      }
      100% {
        opacity: 1;
      }
    }
    @media (prefers-reduced-motion: reduce) {
      .rotar {
        animation: none;
        opacity: 0;
      }
      .rotar:first-child {
        opacity: 1;
      }
    }
  `,
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
        <div class="border-t border-bandline pt-6">
          <h3 class="font-display text-xl font-extrabold">
            Tipos de moto
            <span class="text-bandmuted"
              >· {{ marcaService.marca()?.nombre ?? 'las tres marcas' }}</span
            >
          </h3>
        </div>
        <div class="mt-5 grid gap-4 md:grid-cols-2">
          @for (tipo of tipos(); track tipo.clave) {
            <figure class="tipo overflow-hidden rounded-lg border border-bandline">
              <div class="relative aspect-[16/9]">
                @for (imagen of tipo.imagenes; track imagen.src; let i = $index) {
                  <img
                    class="absolute inset-0 h-full w-full object-cover"
                    [class.rotar]="tipo.imagenes.length > 1"
                    [style.animation-delay]="i * 4 + 's'"
                    [src]="imagen.src"
                    [alt]="imagen.alt"
                    loading="lazy"
                    decoding="async"
                  />
                }
              </div>
              <figcaption
                class="border-t border-bandline px-5 py-3 font-display text-xl font-extrabold"
              >
                {{ tipo.nombre }}
              </figcaption>
            </figure>
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

  protected readonly tipos = computed<TarjetaTipo[]>(() => {
    const elegida = this.marcaService.marca();
    const marcas = elegida ? [elegida] : LISTA_MARCAS;
    return ORDEN_TIPOS.map((tipo) => ({
      clave: tipo,
      nombre: NOMBRE_TIPO[tipo],
      imagenes: marcas.map((marca) => ({
        src: `estilos/${marca.clave}/${CARPETA_TIPO[tipo]}.webp`,
        alt: `Moto tipo ${NOMBRE_TIPO[tipo]} de ${marca.nombre}`,
      })),
    }));
  });

  protected readonly estado = computed(() => {
    const marca = this.marcaService.marca();
    return `Paleta activa: ${marca ? marca.nombre : 'neutra'}`;
  });
}
