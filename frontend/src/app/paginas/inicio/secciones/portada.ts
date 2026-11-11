import {
  Component,
  DestroyRef,
  ElementRef,
  computed,
  inject,
  signal,
  viewChild,
} from '@angular/core';
import { CatalogoService } from '../../../core/catalogo.service';
import { cuotaMensual, licenciaPara } from '../../../core/finanzas';
import { MarcaService } from '../../../core/marca.service';
import { MARCAS, SILUETA_TIPO } from '../../../core/marcas';
import { ClaveMarca } from '../../../core/modelos';
import { UiService } from '../../../core/ui.service';
import { CopPipe } from '../../../shared/cop.pipe';
import { Icono } from '../../../shared/icono';
import { SiluetaMoto } from '../../../shared/silueta-moto';

const INTERVALO = 6500;

function sinMovimiento(): boolean {
  return typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}

@Component({
  selector: 'app-portada',
  imports: [Icono, SiluetaMoto, CopPipe],
  template: `
    <section
      id="inicio"
      class="relative overflow-hidden border-b border-line bg-surface2"
      aria-roledescription="carrusel"
      aria-label="Modelos destacados"
    >
      <div
        class="seigaiha pointer-events-none absolute top-0 -right-10 h-40 w-80 opacity-60"
        aria-hidden="true"
      ></div>
      <div class="gutter mx-auto max-w-7xl py-8 md:py-12">
        <div class="mb-5 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p class="eyebrow text-muted">Concesionario multimarca · Honda · Kawasaki · Yamaha</p>
            <h1
              class="mt-2 max-w-2xl font-display text-3xl leading-tight font-extrabold md:text-[42px]"
            >
              Tres marcas japonesas, un solo asesor para cada una.
            </h1>
          </div>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="grid h-10 w-10 place-items-center rounded-full border border-line bg-surface hover:bg-bg"
              aria-label="Modelo anterior"
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
              aria-label="Modelo siguiente"
              (click)="mover(1)"
            >
              <app-icono nombre="chevron-right" class="h-5 w-5" />
            </button>
          </div>
        </div>

        <div #pista class="carousel flex gap-4 overflow-x-auto" tabindex="0" aria-live="polite">
          @for (item of diapositivas(); track item.moto.id; let i = $index) {
            <article
              class="relative flex w-full shrink-0 flex-col overflow-hidden rounded-xl border border-line bg-surface md:flex-row"
              [style.--mark]="item.marca.color"
              aria-roledescription="diapositiva"
              [attr.aria-label]="
                i +
                1 +
                ' de ' +
                diapositivas().length +
                ': ' +
                item.marca.nombre +
                ' ' +
                item.moto.modelo
              "
            >
              <span
                class="absolute inset-y-0 left-0 w-1"
                [style.background]="item.marca.color"
                aria-hidden="true"
              ></span>
              <div class="flex flex-col justify-between gap-6 p-6 md:w-5/12 md:p-8">
                <div>
                  <p class="eyebrow" [style.color]="item.marca.color">{{ item.marca.nombre }}</p>
                  <h2 class="mt-2 font-display text-3xl leading-tight font-extrabold md:text-4xl">
                    {{ item.moto.modelo }}
                  </h2>
                  <p class="mt-2 max-w-sm text-sm text-muted">{{ item.frase }}</p>
                </div>
                <dl class="flex flex-wrap gap-x-6 gap-y-2 text-sm">
                  <div>
                    <dt class="text-xs text-muted">Cilindraje</dt>
                    <dd class="num font-mono font-semibold">{{ item.moto.cc }} cc</dd>
                  </div>
                  <div>
                    <dt class="text-xs text-muted">Licencia</dt>
                    <dd class="font-mono font-semibold">{{ item.licencia }}</dd>
                  </div>
                  <div>
                    <dt class="text-xs text-muted">Desde</dt>
                    <dd class="num font-mono font-semibold">{{ item.cuota | cop }}/mes</dd>
                  </div>
                </dl>
                <div class="flex flex-wrap gap-2">
                  <button
                    type="button"
                    class="cta inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-bold"
                    (click)="ui.abrirCotizacion(item.moto, 'cotizacion')"
                  >
                    Cotizar
                  </button>
                  <button
                    type="button"
                    class="inline-flex h-10 items-center gap-2 rounded-md border border-line px-4 text-sm font-medium hover:bg-surface2"
                    (click)="ui.abrirCotizacion(item.moto, 'testdrive')"
                  >
                    Pedir test drive
                  </button>
                  <button
                    type="button"
                    class="inline-flex h-10 items-center gap-2 rounded-md border border-line px-4 text-sm font-medium hover:bg-surface2"
                    (click)="verMarca(item.marca.clave)"
                  >
                    Ver {{ item.marca.nombre }}
                  </button>
                </div>
              </div>
              <div class="relative flex-1 bg-surface2/60">
                <span
                  class="vertical pointer-events-none absolute top-4 right-4 font-display text-4xl font-extrabold text-line md:text-6xl"
                  aria-hidden="true"
                  >{{ item.marca.kanji }}</span
                >
                <span
                  class="absolute right-4 bottom-4 grid h-9 w-9 place-items-center rounded-sm font-display text-[11px] leading-none font-extrabold text-white"
                  style="background: var(--seal)"
                  aria-hidden="true"
                  >品<br />質</span
                >
                <div class="mx-auto aspect-[12/7] max-w-[520px] px-6 py-6 text-fg">
                  <app-silueta-moto [tipo]="item.silueta" />
                </div>
              </div>
            </article>
          }
        </div>

        <div
          class="mt-4 flex items-center gap-2"
          role="tablist"
          aria-label="Elegir modelo destacado"
        >
          @for (item of diapositivas(); track item.moto.id; let i = $index) {
            <button
              type="button"
              role="tab"
              class="h-1.5 rounded-full transition-all"
              [style.width.px]="i === actual() ? 32 : 14"
              [style.background]="i === actual() ? 'var(--fg)' : 'var(--line)'"
              [attr.aria-selected]="i === actual()"
              [attr.aria-label]="item.marca.nombre + ' ' + item.moto.modelo"
              (click)="ir(i, true)"
            ></button>
          }
        </div>
      </div>
    </section>
  `,
})
export class Portada {
  protected readonly ui = inject(UiService);
  private readonly catalogo = inject(CatalogoService);
  private readonly marcaService = inject(MarcaService);
  private readonly pista = viewChild.required<ElementRef<HTMLElement>>('pista');

  protected readonly actual = signal(0);
  protected readonly automatico = signal(!sinMovimiento());
  private temporizador: ReturnType<typeof setInterval> | null = null;

  protected readonly diapositivas = computed(() =>
    this.catalogo.destacadas().flatMap((destacada) => {
      const moto = this.catalogo.porId(destacada.motoId);
      if (!moto) {
        return [];
      }
      return [
        {
          moto,
          frase: destacada.frase,
          marca: MARCAS[moto.marca],
          licencia: licenciaPara(moto.cc),
          cuota: cuotaMensual(moto.precio),
          silueta: SILUETA_TIPO[moto.tipo],
        },
      ];
    }),
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
