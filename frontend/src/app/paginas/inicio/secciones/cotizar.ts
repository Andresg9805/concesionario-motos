import { Component, computed, effect, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { map, of, startWith, switchMap } from 'rxjs';
import { AtencionApiService } from '../../../core/atencion-api';
import { FormsModule } from '@angular/forms';
import { FORMATO_CODIGO, PASOS_COTIZACION, PASOS_TEST_DRIVE } from '../../../core/atencion.service';
import { CatalogoService } from '../../../core/catalogo.service';
import { FiltrosService } from '../../../core/filtros.service';
import { formatoCop, leerPesos, precioMaximoPorCuota } from '../../../core/finanzas';
import { MarcaService } from '../../../core/marca.service';
import { MARCAS } from '../../../core/marcas';
import { Atencion, CategoriaLicencia } from '../../../core/modelos';
import { UiService } from '../../../core/ui.service';
import { Icono } from '../../../shared/icono';

@Component({
  selector: 'app-cotizar',
  imports: [FormsModule, Icono],
  template: `
    <section
      id="cotizar"
      class="gutter relative mx-auto max-w-7xl py-14"
      aria-labelledby="tituloCotizar"
    >
      <div
        class="seigaiha pointer-events-none absolute top-6 right-0 h-32 w-72 opacity-40"
        aria-hidden="true"
      ></div>
      <p class="eyebrow eyebrow-marca text-muted">Paso 3</p>
      <h2 id="tituloCotizar" class="mt-1 font-display text-2xl font-extrabold md:text-3xl">
        Cotiza sin crear cuenta
      </h2>
      <p class="mt-1 max-w-2xl text-sm text-muted">
        Calcula qué moto alcanzas con tu cuota mensual, o consulta el estado de una cotización o
        test drive con tu código CM-XXXX.
      </p>
      <div class="relative mt-6 grid gap-4 lg:grid-cols-5">
        <form
          class="rounded-lg border border-line bg-surface p-5 lg:col-span-3"
          novalidate
          (ngSubmit)="buscarPorCuota()"
        >
          <h3 class="flex items-center gap-2 font-display text-lg font-extrabold">
            <app-icono nombre="wallet" class="h-5 w-5" />Buscar por cuota
          </h3>
          <div class="mt-4 grid gap-4 sm:grid-cols-2">
            <label class="text-sm font-medium" for="bcCuota"
              >Cuota mensual máxima (COP)
              <input
                id="bcCuota"
                name="cuota"
                inputmode="numeric"
                class="field num mt-1 h-11 w-full rounded-md px-3"
                [attr.aria-invalid]="!!errorCuota()"
                aria-describedby="bcCuotaErr"
                [(ngModel)]="cuota"
              />
              @if (errorCuota()) {
                <span id="bcCuotaErr" class="mt-1 block text-xs text-danger">{{
                  errorCuota()
                }}</span>
              }
            </label>
            <label class="text-sm font-medium" for="bcInicial"
              >Cuota inicial (COP)
              <input
                id="bcInicial"
                name="inicial"
                inputmode="numeric"
                class="field num mt-1 h-11 w-full rounded-md px-3"
                [(ngModel)]="inicial"
              />
            </label>
            <label class="text-sm font-medium" for="bcPlazo"
              >Plazo
              <select
                id="bcPlazo"
                name="plazo"
                class="field mt-1 h-11 w-full rounded-md px-3"
                [(ngModel)]="plazo"
              >
                @for (meses of plazos; track meses) {
                  <option [ngValue]="meses">{{ meses }} meses</option>
                }
              </select>
            </label>
            <fieldset class="text-sm font-medium">
              <legend>Tu licencia</legend>
              <div class="mt-1 grid grid-cols-2 gap-2">
                <label
                  class="flex h-11 cursor-pointer items-center gap-2 rounded-md border border-line px-3 has-[:checked]:border-accent has-[:checked]:bg-accentsoft"
                  ><input type="radio" name="licencia" value="A1" [(ngModel)]="licencia" /> A1 ·
                  hasta 125 cc</label
                >
                <label
                  class="flex h-11 cursor-pointer items-center gap-2 rounded-md border border-line px-3 has-[:checked]:border-accent has-[:checked]:bg-accentsoft"
                  ><input type="radio" name="licencia" value="A2" [(ngModel)]="licencia" /> A2 ·
                  cualquier moto</label
                >
              </div>
            </fieldset>
          </div>
          <div class="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="submit"
              class="cta inline-flex h-11 items-center gap-2 rounded-md px-5 text-sm font-bold"
            >
              <app-icono nombre="search" class="h-4 w-4" />Ver motos que alcanzo
            </button>
            <p class="num text-sm text-muted" aria-live="polite">{{ resultadoCuota() }}</p>
          </div>
        </form>

        <form
          class="rounded-lg border border-line bg-surface p-5 lg:col-span-2"
          novalidate
          (ngSubmit)="consultar()"
        >
          <h3 class="flex items-center gap-2 font-display text-lg font-extrabold">
            <app-icono nombre="scan-search" class="h-5 w-5" />Seguimiento con código
          </h3>
          <label class="mt-4 block text-sm font-medium" for="codigo"
            >Código de atención
            <input
              id="codigo"
              name="codigo"
              autocomplete="off"
              maxlength="7"
              class="field mt-1 h-11 w-full rounded-md px-3 font-mono tracking-widest uppercase"
              placeholder="CM-XXXX"
              [attr.aria-invalid]="!!errorCodigo()"
              [ngModel]="codigo()"
              (ngModelChange)="escribirCodigo($event)"
            />
          </label>
          <p class="mt-1 text-xs text-muted">
            Código de ejemplo:
            <button
              type="button"
              class="font-mono underline underline-offset-2"
              (click)="usarEjemplo()"
            >
              CM-7K2Q
            </button>
          </p>
          @if (errorCodigo()) {
            <p class="mt-1 text-xs text-danger">{{ errorCodigo() }}</p>
          }
          <button
            type="submit"
            class="matte-btn mt-4 inline-flex h-11 items-center gap-2 rounded-md px-5 text-sm font-bold"
          >
            Consultar estado
          </button>
          @if (consultado()) {
            <div
              class="mt-4 rounded-md border border-line bg-surface2 p-4 text-sm"
              aria-live="polite"
            >
              @if (buscando()) {
                <p class="text-muted">Buscando el código…</p>
              } @else if (encontrada(); as atencion) {
                <div class="flex flex-wrap items-baseline justify-between gap-2">
                  <p class="font-mono text-base font-semibold">{{ atencion.codigo }}</p>
                  <span
                    class="rounded bg-accentsoft px-2 py-0.5 font-mono text-xs font-semibold text-accenttext"
                    >{{ atencion.estado }}</span
                  >
                </div>
                <p class="mt-1 text-muted">
                  {{ atencion.tipo === 'testdrive' ? 'Test drive' : 'Cotización' }} ·
                  {{ nombreMarca(atencion) }} {{ atencion.moto }} · Asesor:
                  {{ atencion.asesor.nombre }}{{ atencion.ejemplo ? ' · código de ejemplo' : '' }}
                </p>
                <ol class="mt-3 flex flex-wrap gap-1.5">
                  @for (paso of pasos(); track paso; let i = $index) {
                    <li
                      class="rounded px-2 py-0.5 font-mono text-[11px]"
                      [class]="
                        i <= indicePaso() ? 'bg-fg text-bg' : 'border border-line text-muted'
                      "
                    >
                      {{ paso }}
                    </li>
                  }
                </ol>
              } @else {
                <p class="font-bold">No encontramos el código {{ consultado() }}.</p>
                <p class="mt-1 text-muted">
                  Revisa que esté igual al que recibiste al cotizar o pedir el test drive.
                </p>
              }
            </div>
          }
        </form>
      </div>
    </section>
  `,
})
export class Cotizar {
  private readonly filtros = inject(FiltrosService);
  private readonly catalogo = inject(CatalogoService);
  private readonly marcaService = inject(MarcaService);
  private readonly atencionApi = inject(AtencionApiService);
  private readonly ui = inject(UiService);

  protected readonly plazos = [12, 24, 36, 48, 60];
  protected cuota = '450.000';
  protected inicial = '1.500.000';
  protected plazo = 36;
  protected licencia: CategoriaLicencia = 'A1';

  protected readonly errorCuota = signal('');
  protected readonly resultadoCuota = signal('');
  protected readonly codigo = signal('');
  protected readonly errorCodigo = signal('');
  protected readonly consultado = signal<string | null>(null);

  private readonly intento = signal(0);
  private readonly busqueda = toSignal(
    toObservable(computed(() => ({ codigo: this.consultado(), intento: this.intento() }))).pipe(
      switchMap(({ codigo }) =>
        codigo
          ? this.atencionApi.buscar(codigo).pipe(
              map((atencion) => ({ buscando: false, atencion })),
              startWith({ buscando: true, atencion: undefined as Atencion | undefined }),
            )
          : of({ buscando: false, atencion: undefined as Atencion | undefined }),
      ),
    ),
    { initialValue: { buscando: false, atencion: undefined as Atencion | undefined } },
  );
  protected readonly buscando = computed(() => this.busqueda().buscando);
  protected readonly encontrada = computed(() => this.busqueda().atencion);

  protected readonly pasos = computed(() =>
    this.encontrada()?.tipo === 'testdrive' ? PASOS_TEST_DRIVE : PASOS_COTIZACION,
  );
  protected readonly indicePaso = computed(() =>
    this.pasos().indexOf(this.encontrada()?.estado ?? ''),
  );

  constructor() {
    effect(() => {
      const pedido = this.ui.codigoBuscado();
      if (pedido) {
        this.codigo.set(pedido);
        this.consultar();
        this.ui.codigoBuscado.set(null);
        document.getElementById('cotizar')?.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }

  protected buscarPorCuota(): void {
    const cuota = leerPesos(this.cuota);
    if (cuota < 100_000) {
      this.errorCuota.set('Escribe una cuota de al menos $100.000.');
      return;
    }
    this.errorCuota.set('');
    const maximo = precioMaximoPorCuota(cuota, leerPesos(this.inicial), this.plazo);
    this.filtros.precioMaximo.set(maximo);
    this.filtros.rango.set('todos');
    this.filtros.segmento.set(this.licencia === 'A1' ? 'a1' : 'todas');
    const total = this.filtros.aplicar(this.catalogo.porMarca(this.marcaService.actual())).length;
    this.resultadoCuota.set(
      `Alcanzas motos de hasta ${formatoCop(maximo)}: ${total} ${total === 1 ? 'opción' : 'opciones'}.`,
    );
    setTimeout(
      () => document.getElementById('catalogo')?.scrollIntoView({ behavior: 'smooth' }),
      400,
    );
  }

  protected escribirCodigo(valor: string): void {
    let limpio = valor.toUpperCase().replace(/[^A-Z0-9-]/g, '');
    if (/^CM[A-Z0-9]/.test(limpio)) {
      limpio = 'CM-' + limpio.slice(2);
    }
    this.codigo.set(limpio.slice(0, 7));
  }

  protected usarEjemplo(): void {
    this.codigo.set('CM-7K2Q');
    this.consultar();
  }

  protected consultar(): void {
    const codigo = this.codigo().trim().toUpperCase();
    if (!FORMATO_CODIGO.test(codigo)) {
      this.errorCodigo.set('Escribe el código con el formato CM-XXXX, por ejemplo CM-7K2Q.');
      this.consultado.set(null);
      return;
    }
    this.errorCodigo.set('');
    this.consultado.set(codigo);
    this.intento.update((n) => n + 1);
  }

  protected nombreMarca(atencion: Atencion): string {
    return MARCAS[atencion.marca].nombre;
  }
}
