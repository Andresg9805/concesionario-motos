import {
  Component,
  DestroyRef,
  ElementRef,
  computed,
  inject,
  signal,
  viewChild,
} from '@angular/core';
import { MarcaService } from '../../../core/marca.service';
import { MARCAS } from '../../../core/marcas';
import { ClaveMarca } from '../../../core/modelos';
import { Icono } from '../../../shared/icono';

const INTERVALO = 6500;

export const BANNERS: readonly { clave: ClaveMarca; src: string; alt: string }[] = [
  {
    clave: 'honda',
    src: '/carrusel/honda.webp',
    alt: 'Moto deportiva Honda en una carretera de montaña',
  },
  {
    clave: 'kawasaki',
    src: '/carrusel/kawasaki.webp',
    alt: 'Moto Kawasaki Ninja tomando una curva en la carretera',
  },
  {
    clave: 'yamaha',
    src: '/carrusel/yamaha.webp',
    alt: 'Yamaha YZF-R1 en una carretera al atardecer',
  },
];

function sinMovimiento(): boolean {
  return typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}

@Component({
  selector: 'app-portada',
  imports: [Icono],
  template: `
    <section
      id="inicio"
      class="relative overflow-hidden border-b border-line bg-surface2"
      aria-roledescription="carrusel"
      aria-label="Nuestras marcas"
    >
      <div class="resplandor pointer-events-none absolute inset-0" aria-hidden="true"></div>
      <div
        class="seigaiha pointer-events-none absolute top-0 -right-10 h-40 w-80 opacity-60"
        aria-hidden="true"
      ></div>
      <div class="gutter mx-auto max-w-7xl py-8 md:py-12">
        <div class="mb-5 flex flex-wrap items-end justify-between gap-x-6 gap-y-4 md:flex-nowrap">
          <div class="min-w-0 basis-full md:flex-1">
            <p class="eyebrow eyebrow-marca text-muted">
              Concesionario multimarca · Honda · Kawasaki · Yamaha
            </p>
            <h1
              class="mt-2 font-display text-3xl leading-tight font-extrabold text-balance md:text-4xl xl:text-[42px] xl:whitespace-nowrap"
            >
              Tres leyendas japonesas, una sola pasión.
            </h1>
          </div>
          <div class="flex shrink-0 items-center gap-2">
            <button
              type="button"
              class="grid h-10 w-10 place-items-center rounded-full border border-line bg-surface hover:bg-bg"
              aria-label="Imagen anterior"
              (click)="mover(-1)"
            >
              <app-icono nombre="chevron-left" class="h-5 w-5" />
            </button>
            <button
              type="button"
              class="grid h-10 w-10 place-items-center rounded-full border border-line bg-surface hover:bg-bg"
              [attr.aria-label]="automatico() ? 'Pausar carrusel' : 'Reanudar carrusel'"
              (click)="alternarAutomatico()"
            >
              <app-icono [nombre]="automatico() ? 'pause' : 'play'" class="h-4 w-4" />
            </button>
            <button
              type="button"
              class="grid h-10 w-10 place-items-center rounded-full border border-line bg-surface hover:bg-bg"
              aria-label="Imagen siguiente"
              (click)="mover(1)"
            >
              <app-icono nombre="chevron-right" class="h-5 w-5" />
            </button>
          </div>
        </div>

        <div #pista class="carousel flex gap-4 overflow-x-auto" tabindex="0" aria-live="polite">
          @for (item of diapositivas(); track item.clave; let i = $index) {
            <article
              class="relative w-full shrink-0 overflow-hidden rounded-xl border border-line"
              [style.--mark]="item.marca.color"
              aria-roledescription="diapositiva"
              [attr.aria-label]="i + 1 + ' de ' + diapositivas().length + ': ' + item.marca.nombre"
            >
              <button
                type="button"
                class="group block w-full"
                [attr.aria-label]="'Ver motos ' + item.marca.nombre"
                (click)="verMarca(item.clave)"
              >
                <img
                  [src]="item.src"
                  [alt]="item.alt"
                  class="aspect-[1920/596] w-full object-cover transition-transform duration-500 motion-safe:group-hover:scale-[1.02]"
                  [attr.loading]="i === 0 ? 'eager' : 'lazy'"
                  decoding="async"
                />
                <span
                  class="absolute right-2 bottom-2 inline-flex h-8 items-center gap-2 rounded-md bg-black/70 px-3 text-xs font-bold text-white shadow-lg backdrop-blur-sm md:right-4 md:bottom-4 md:h-10 md:px-4 md:text-sm"
                >
                  <span
                    class="h-2.5 w-2.5 rounded-full"
                    [style.background]="item.marca.color"
                  ></span>
                  Ver {{ item.marca.nombre }}
                  <app-icono nombre="arrow-right" class="h-4 w-4" />
                </span>
              </button>
            </article>
          }
        </div>

        <div class="mt-4 flex items-center gap-2" role="tablist" aria-label="Elegir marca">
          @for (item of diapositivas(); track item.clave; let i = $index) {
            <button
              type="button"
              role="tab"
              class="h-1.5 rounded-full transition-all"
              [style.width.px]="i === actual() ? 32 : 14"
              [style.background]="i === actual() ? 'var(--fg)' : 'var(--line)'"
              [attr.aria-selected]="i === actual()"
              [attr.aria-label]="item.marca.nombre"
              (click)="ir(i, true)"
            ></button>
          }
        </div>
      </div>
    </section>
  `,
})
export class Portada {
  private readonly marcaService = inject(MarcaService);
  private readonly pista = viewChild.required<ElementRef<HTMLElement>>('pista');

  protected readonly actual = signal(0);
  protected readonly automatico = signal(!sinMovimiento());
  private temporizador: ReturnType<typeof setInterval> | null = null;

  protected readonly diapositivas = computed(() =>
    BANNERS.map((banner) => ({ ...banner, marca: MARCAS[banner.clave] })),
  );

  constructor() {
    this.iniciar();
    inject(DestroyRef).onDestroy(() => this.detener());
  }

  protected mover(paso: number): void {
    this.ir(this.actual() + paso, true);
  }

  protected ir(indice: number, reiniciar = false): void {
    const total = this.diapositivas().length;
    if (total === 0) {
      return;
    }
    const nuevo = (indice + total) % total;
    this.actual.set(nuevo);
    const pista = this.pista().nativeElement;
    const diapositiva = pista.children[nuevo] as HTMLElement | undefined;
    if (diapositiva) {
      pista.scrollTo({
        left: diapositiva.offsetLeft - pista.offsetLeft,
        behavior: sinMovimiento() ? 'auto' : 'smooth',
      });
    }
    if (reiniciar) {
      this.iniciar();
    }
  }

  protected alternarAutomatico(): void {
    this.automatico.update((valor) => !valor);
    this.iniciar();
  }

  protected verMarca(clave: ClaveMarca): void {
    this.marcaService.elegir(clave);
    document
      .getElementById('marcas')
      ?.scrollIntoView({ behavior: sinMovimiento() ? 'auto' : 'smooth' });
  }

  private iniciar(): void {
    this.detener();
    if (this.automatico()) {
      this.temporizador = setInterval(() => this.ir(this.actual() + 1), INTERVALO);
    }
  }

  private detener(): void {
    if (this.temporizador) {
      clearInterval(this.temporizador);
    }
    this.temporizador = null;
  }
}
