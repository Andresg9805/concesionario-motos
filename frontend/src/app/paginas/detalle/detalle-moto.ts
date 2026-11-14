import { Component, computed, inject, input, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { Observable, catchError, debounceTime, map, of, startWith, switchMap } from 'rxjs';
import { MARCAS, NOMBRE_TIPO, SILUETA_TIPO } from '../../core/marcas';
import {
  ConsultaCostoReal,
  CostoRealApi,
  MotoDetalleApi,
  MotosApiService,
  PLAZO_MAXIMO,
  PLAZO_MINIMO,
  UsoMoto,
  claveDeMarca,
  motoDesdeApi,
} from '../../core/motos-api';
import { CatalogoService } from '../../core/catalogo.service';
import { UiService } from '../../core/ui.service';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';
import { SiluetaMoto } from '../../shared/silueta-moto';

type Estado<T> = { estado: 'cargando' } | { estado: 'error' } | { estado: 'listo'; dato: T };

interface Rubro {
  nombre: string;
  valor: number;
  color: string;
}

const PLAZOS = [12, 24, 36, 48, 60, 72].filter((p) => p >= PLAZO_MINIMO && p <= PLAZO_MAXIMO);

const USOS: { id: UsoMoto; texto: string }[] = [
  { id: 'CIUDAD', texto: 'Ciudad' },
  { id: 'CARRETERA', texto: 'Carretera' },
  { id: 'TRABAJO', texto: 'Trabajo' },
];

@Component({
  selector: 'app-detalle-moto',
  imports: [RouterLink, SiluetaMoto, Icono, CopPipe],
  template: `
    <div class="gutter mx-auto max-w-7xl py-10">
      <a
        routerLink="/"
        fragment="catalogo"
        class="inline-flex items-center gap-1 text-sm font-medium text-muted hover:text-fg"
        ><app-icono nombre="arrow-left" class="h-4 w-4" /> Volver al catálogo</a
      >

      @switch (moto().estado) {
        @case ('cargando') {
          <div class="mt-6 h-72 animate-pulse rounded-lg bg-surface2" aria-busy="true"></div>
        }
        @case ('error') {
          <div
            class="mt-6 flex flex-col items-start gap-3 rounded-lg border border-dashed border-line p-8"
            role="alert"
          >
            <p class="font-display text-lg font-extrabold">No pudimos cargar esta moto.</p>
            <p class="text-sm text-muted">
              Revisa que el servidor esté encendido o vuelve al catálogo y elige otra.
            </p>
            <button
              type="button"
              class="cta inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-bold"
              (click)="reintentar()"
            >
              <app-icono nombre="refresh-cw" class="h-4 w-4" /> Reintentar
            </button>
          </div>
        }
        @case ('listo') {
          @if (detalle(); as m) {
            <section
              class="mt-6 grid gap-6 lg:grid-cols-[1.1fr_1fr]"
              [style.--mark]="colorMarca()"
              aria-labelledby="tituloMoto"
            >
              <div class="relative rounded-lg border border-line bg-surface2 px-8 pt-10 pb-6">
                <span
                  class="absolute top-4 left-4 rounded bg-surface px-2 py-0.5 text-[11px] font-bold"
                  >{{ tipo() }}</span
                >
                <app-silueta-moto [tipo]="silueta()" />
              </div>
              <div class="flex flex-col gap-4">
                <div>
                  <p class="flex items-center gap-1.5 text-sm text-muted">
                    <span class="h-2 w-2 rounded-full" [style.background]="colorMarca()"></span>
                    {{ m.marca.nombre }} · {{ m.anio }}
                  </p>
                  <h1 id="tituloMoto" class="mt-1 font-display text-3xl font-extrabold md:text-4xl">
                    {{ m.modelo }}
                  </h1>
                  <p class="mt-2 text-sm text-muted">{{ m.descripcion }}</p>
                </div>
                <dl class="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  <div class="rounded-md border border-line p-3">
                    <dt class="text-xs text-muted">Cilindraje</dt>
                    <dd class="num font-bold">{{ m.cilindraje_cc }} cc</dd>
                  </div>
                  <div class="rounded-md border border-line p-3">
                    <dt class="text-xs text-muted">Licencia</dt>
                    <dd class="num font-bold">{{ m.categoria_licencia }}</dd>
                  </div>
                  <div class="rounded-md border border-line p-3">
                    <dt class="text-xs text-muted">Rinde</dt>
                    <dd class="num font-bold">{{ m.consumo_km_galon }} km/gal</dd>
                  </div>
                  <div class="rounded-md border border-line p-3">
                    <dt class="text-xs text-muted">Disponible</dt>
                    <dd class="font-bold">{{ m.disponible ? 'Sí' : 'Agotada' }}</dd>
                  </div>
                </dl>
                <div>
                  <p class="text-xs text-muted">Precio de referencia</p>
                  <p class="num font-display text-3xl font-extrabold">{{ m.precio_cop | cop }}</p>
                </div>
                <div class="grid grid-cols-2 gap-2 sm:max-w-sm">
                  <button
                    type="button"
                    class="cta inline-flex h-11 items-center justify-center gap-2 rounded-md text-sm font-bold"
                    (click)="abrir('cotizacion')"
                  >
                    <app-icono nombre="file-text" class="h-4 w-4" />Cotizar
                  </button>
                  <button
                    type="button"
                    class="inline-flex h-11 items-center justify-center gap-2 rounded-md border border-line text-sm font-bold hover:bg-surface2"
                    (click)="abrir('testdrive')"
                  >
                    <app-icono nombre="flag" class="h-4 w-4" />Test drive
                  </button>
                </div>
              </div>
            </section>

            <section class="mt-12" aria-labelledby="tituloCosto">
              <p class="eyebrow eyebrow-marca text-muted">Costo real</p>
              <h2 id="tituloCosto" class="mt-1 font-display text-2xl font-extrabold md:text-3xl">
                ¿Cuánto cuesta tenerla de verdad?
              </h2>
              <p class="mt-1 max-w-2xl text-sm text-muted">
                Además de la cuota, una moto gasta gasolina, SOAT, impuesto y mantenimiento. Ajusta
                cómo la vas a usar y mira cuánto pagarías en total cada mes.
              </p>

              <div class="mt-6 grid gap-6 lg:grid-cols-[340px_1fr]">
                <form
                  class="flex flex-col gap-5 self-start rounded-lg border border-line bg-surface p-5 lg:sticky lg:top-24"
                  (submit)="$event.preventDefault()"
                >
                  <div>
                    <label for="km" class="flex justify-between text-sm font-medium"
                      >Kilómetros al mes <span class="num">{{ kmMes() }} km</span></label
                    >
                    <input
                      id="km"
                      type="range"
                      min="100"
                      max="5000"
                      step="100"
                      class="mt-2 w-full accent-[var(--accent)]"
                      [value]="kmMes()"
                      (input)="kmMes.set(numero($event))"
                    />
                  </div>

                  <fieldset>
                    <legend class="text-sm font-medium">Uso principal</legend>
                    <div class="mt-2 grid grid-cols-3 gap-1 rounded-md border border-line p-1">
                      @for (u of usos; track u.id) {
                        <button
                          type="button"
                          class="tab h-9 rounded text-sm font-medium"
                          [attr.aria-selected]="uso() === u.id"
                          (click)="uso.set(u.id)"
                        >
                          {{ u.texto }}
                        </button>
                      }
                    </div>
                  </fieldset>

                  <div>
                    <label for="inicial" class="text-sm font-medium">Cuota inicial</label>
                    <input
                      id="inicial"
                      type="number"
                      min="0"
                      step="100000"
                      inputmode="numeric"
                      class="field num mt-1 h-11 w-full rounded-md px-3"
                      [value]="cuotaInicial()"
                      (input)="cuotaInicial.set(numero($event))"
                    />
                    <p class="mt-1 text-xs text-muted">{{ cuotaInicial() | cop }}</p>
                  </div>

                  <div>
                    <label for="plazo" class="text-sm font-medium">Plazo</label>
                    <select
                      id="plazo"
                      class="field mt-1 h-11 w-full rounded-md px-3"
                      [value]="plazo()"
                      (change)="plazo.set(numero($event))"
                    >
                      @for (p of plazos; track p) {
                        <option [value]="p" [selected]="p === plazo()">{{ p }} meses</option>
                      }
                    </select>
                  </div>

                  <div class="border-t border-line pt-4">
                    <label class="flex items-center gap-2 text-sm font-medium">
                      <input
                        type="checkbox"
                        class="h-4 w-4 accent-[var(--accent)]"
                        [checked]="trabajo()"
                        (change)="trabajo.set(marcado($event))"
                      />
                      La voy a usar para trabajar
                    </label>
                    @if (trabajo()) {
                      <div class="mt-3 grid grid-cols-2 gap-3">
                        <div>
                          <label for="ganancia" class="text-xs text-muted">Ganancia por día</label>
                          <input
                            id="ganancia"
                            type="number"
                            min="0"
                            step="5000"
                            inputmode="numeric"
                            class="field num mt-1 h-10 w-full rounded-md px-3"
                            [value]="gananciaDiaria()"
                            (input)="gananciaDiaria.set(numero($event))"
                          />
                        </div>
                        <div>
                          <label for="dias" class="text-xs text-muted">Días al mes</label>
                          <input
                            id="dias"
                            type="number"
                            min="0"
                            max="31"
                            inputmode="numeric"
                            class="field num mt-1 h-10 w-full rounded-md px-3"
                            [value]="diasTrabajo()"
                            (input)="diasTrabajo.set(numero($event))"
                          />
                        </div>
                      </div>
                    }
                  </div>
                </form>

                <div aria-live="polite">
                  @switch (costo().estado) {
                    @case ('cargando') {
                      <div class="h-80 animate-pulse rounded-lg bg-surface2"></div>
                    }
                    @case ('error') {
                      <p
                        class="rounded-lg border border-dashed border-line p-6 text-sm text-muted"
                        role="alert"
                      >
                        No pudimos calcular el costo con esos datos. Revisa la cuota inicial: no
                        puede ser mayor que el precio de la moto.
                      </p>
                    }
                    @case ('listo') {
                      @if (resultado(); as r) {
                        <div class="flex flex-col gap-4">
                          <div class="rounded-lg border border-accent bg-surface p-5">
                            <p class="text-sm text-muted">Total al mes</p>
                            <p class="num font-display text-4xl font-extrabold">
                              {{ r.mensual.total_cop | cop }}
                            </p>
                            <div
                              class="mt-4 flex h-3 overflow-hidden rounded-full bg-surface2"
                              aria-hidden="true"
                            >
                              @for (rubro of rubros(); track rubro.nombre) {
                                <span
                                  class="h-full"
                                  [style.width.%]="porcentaje(rubro.valor, r.mensual.total_cop)"
                                  [style.background]="rubro.color"
                                ></span>
                              }
                            </div>
                            <ul class="mt-4 grid gap-2 text-sm sm:grid-cols-2">
                              @for (rubro of rubros(); track rubro.nombre) {
                                <li class="flex items-center justify-between gap-3">
                                  <span class="flex items-center gap-2 text-muted"
                                    ><span
                                      class="h-2.5 w-2.5 rounded-sm"
                                      [style.background]="rubro.color"
                                    ></span
                                    >{{ rubro.nombre }}</span
                                  >
                                  <span class="num font-medium">{{ rubro.valor | cop }}</span>
                                </li>
                              }
                            </ul>
                          </div>

                          <div class="grid gap-4 md:grid-cols-2">
                            <div class="rounded-lg border border-line bg-surface p-5">
                              <h3 class="font-display text-lg font-extrabold">Para sacarla</h3>
                              <dl class="mt-3 flex flex-col gap-1.5 text-sm">
                                <div class="flex justify-between">
                                  <dt class="text-muted">Precio de lista</dt>
                                  <dd class="num">{{ r.adquisicion.precio_lista_cop | cop }}</dd>
                                </div>
                                <div class="flex justify-between">
                                  <dt class="text-muted">Matrícula</dt>
                                  <dd class="num">{{ r.adquisicion.matricula_cop | cop }}</dd>
                                </div>
                                <div class="flex justify-between">
                                  <dt class="text-muted">SOAT del primer año</dt>
                                  <dd class="num">{{ r.adquisicion.soat_cop | cop }}</dd>
                                </div>
                                <div class="flex justify-between">
                                  <dt class="text-muted">Impuesto</dt>
                                  <dd class="num">{{ r.adquisicion.impuesto_cop | cop }}</dd>
                                </div>
                                <div class="flex justify-between">
                                  <dt class="text-muted">Trámites</dt>
                                  <dd class="num">{{ r.adquisicion.tramites_cop | cop }}</dd>
                                </div>
                                <div class="mt-1 flex justify-between border-t border-line pt-2">
                                  <dt class="font-bold">Total</dt>
                                  <dd class="num font-bold">
                                    {{ r.adquisicion.total_cop | cop }}
                                  </dd>
                                </div>
                              </dl>
                            </div>

                            <div class="rounded-lg border border-line bg-surface p-5">
                              <h3 class="font-display text-lg font-extrabold">Crédito</h3>
                              <dl class="mt-3 flex flex-col gap-1.5 text-sm">
                                <div class="flex justify-between">
                                  <dt class="text-muted">Cuota inicial</dt>
                                  <dd class="num">
                                    {{ r.financiacion.cuota_inicial_cop | cop }}
                                  </dd>
                                </div>
                                <div class="flex justify-between">
                                  <dt class="text-muted">Monto financiado</dt>
                                  <dd class="num">
                                    {{ r.financiacion.monto_financiado_cop | cop }}
                                  </dd>
                                </div>
                                <div class="flex justify-between">
                                  <dt class="text-muted">Plazo</dt>
                                  <dd class="num">{{ r.financiacion.plazo_meses }} meses</dd>
                                </div>
                                <div class="flex justify-between">
                                  <dt class="text-muted">Tasa mensual</dt>
                                  <dd class="num">{{ tasa(r.financiacion.tasa_mensual) }}</dd>
                                </div>
                                <div class="mt-1 flex justify-between border-t border-line pt-2">
                                  <dt class="font-bold">Cuota</dt>
                                  <dd class="num font-bold">
                                    {{ r.financiacion.cuota_mensual_cop | cop }}
                                  </dd>
                                </div>
                              </dl>
                            </div>
                          </div>

                          @if (r.modo_trabajo; as t) {
                            <div class="rounded-lg border border-line bg-surface p-5">
                              <h3
                                class="flex items-center gap-2 font-display text-lg font-extrabold"
                              >
                                <app-icono nombre="briefcase" class="h-5 w-5" /> Modo trabajo
                              </h3>
                              <dl class="mt-3 grid gap-3 text-sm sm:grid-cols-3">
                                <div>
                                  <dt class="text-muted">Ganas al mes</dt>
                                  <dd class="num text-lg font-bold">
                                    {{ t.ganancia_mensual_cop | cop }}
                                  </dd>
                                </div>
                                <div>
                                  <dt class="text-muted">Te queda después de gastos</dt>
                                  <dd
                                    class="num text-lg font-bold"
                                    [class.text-red-500]="t.ganancia_neta_mensual_cop < 0"
                                  >
                                    {{ t.ganancia_neta_mensual_cop | cop }}
                                  </dd>
                                </div>
                                <div>
                                  <dt class="text-muted">Se paga sola en</dt>
                                  <dd class="num text-lg font-bold">
                                    @if (t.meses_para_pagarse !== null) {
                                      {{ t.meses_para_pagarse }}
                                      {{ t.meses_para_pagarse === 1 ? 'mes' : 'meses' }}
                                    } @else {
                                      No alcanza
                                    }
                                  </dd>
                                </div>
                              </dl>
                            </div>
                          }

                          <p class="text-xs text-muted">
                            Valores de referencia calculados con los parámetros de la tienda. El
                            valor final lo confirma el asesor.
                          </p>
                        </div>
                      }
                    }
                  }
                </div>
              </div>
            </section>
          }
        }
      }
    </div>
  `,
})
export class DetalleMoto {
  readonly id = input.required<string>();

  private readonly api = inject(MotosApiService);
  private readonly catalogo = inject(CatalogoService);
  private readonly ui = inject(UiService);

  protected readonly usos = USOS;
  protected readonly plazos = PLAZOS;

  protected readonly kmMes = signal(800);
  protected readonly uso = signal<UsoMoto>('CIUDAD');
  protected readonly cuotaInicial = signal(0);
  protected readonly plazo = signal(36);
  protected readonly trabajo = signal(false);
  protected readonly gananciaDiaria = signal(80000);
  protected readonly diasTrabajo = signal(24);

  private readonly intento = signal(0);

  protected readonly moto = toSignal(
    toObservable(computed(() => ({ id: this.id(), intento: this.intento() }))).pipe(
      switchMap(({ id }) =>
        this.buscar(id).pipe(
          map((dato): Estado<MotoDetalleApi> => ({ estado: 'listo', dato })),
          catchError(() => of<Estado<MotoDetalleApi>>({ estado: 'error' })),
          startWith<Estado<MotoDetalleApi>>({ estado: 'cargando' }),
        ),
      ),
    ),
    { initialValue: { estado: 'cargando' } as Estado<MotoDetalleApi> },
  );

  protected readonly detalle = computed(() => {
    const estado = this.moto();
    return estado.estado === 'listo' ? estado.dato : null;
  });

  private readonly consulta = computed<{ id: number; datos: ConsultaCostoReal } | null>(() => {
    const moto = this.detalle();
    if (!moto) {
      return null;
    }
    const trabajo = this.trabajo();
    return {
      id: moto.id,
      datos: {
        km_mes: this.kmMes(),
        uso: this.uso(),
        cuota_inicial_cop: Math.max(0, this.cuotaInicial()),
        plazo_meses: this.plazo(),
        ganancia_diaria_cop: trabajo ? Math.max(0, this.gananciaDiaria()) : 0,
        dias_trabajo_mes: trabajo ? Math.min(31, Math.max(0, this.diasTrabajo())) : 0,
      },
    };
  });

  protected readonly costo = toSignal(
    toObservable(this.consulta).pipe(
      debounceTime(250),
      switchMap((consulta) =>
        consulta === null
          ? of<Estado<CostoRealApi>>({ estado: 'cargando' })
          : this.api.costoReal(String(consulta.id), consulta.datos).pipe(
              map((dato): Estado<CostoRealApi> => ({ estado: 'listo', dato })),
              catchError(() => of<Estado<CostoRealApi>>({ estado: 'error' })),
            ),
      ),
    ),
    { initialValue: { estado: 'cargando' } as Estado<CostoRealApi> },
  );

  protected readonly resultado = computed(() => {
    const estado = this.costo();
    return estado.estado === 'listo' ? estado.dato : null;
  });

  protected readonly rubros = computed<Rubro[]>(() => {
    const r = this.resultado();
    if (!r) {
      return [];
    }
    return [
      { nombre: 'Cuota del crédito', valor: r.mensual.cuota_credito_cop, color: 'var(--accent)' },
      { nombre: 'Gasolina', valor: r.mensual.gasolina_cop, color: '#f59e0b' },
      { nombre: 'Mantenimiento', valor: r.mensual.mantenimiento_cop, color: '#14b8a6' },
      { nombre: 'SOAT', valor: r.mensual.soat_cop, color: '#8b5cf6' },
      { nombre: 'Impuesto', valor: r.mensual.impuesto_cop, color: '#64748b' },
    ];
  });

  protected readonly colorMarca = computed(() => {
    const moto = this.detalle();
    return moto ? MARCAS[claveDeMarca(moto.marca)].color : 'var(--accent)';
  });
  protected readonly tipo = computed(() => {
    const moto = this.detalle();
    return moto ? NOMBRE_TIPO[moto.tipo] : '';
  });
  protected readonly silueta = computed(() => {
    const moto = this.detalle();
    return moto ? SILUETA_TIPO[moto.tipo] : 'naked';
  });

  protected reintentar(): void {
    this.intento.update((n) => n + 1);
  }

  protected abrir(tipo: 'cotizacion' | 'testdrive'): void {
    const moto = this.detalle();
    if (moto) {
      this.ui.abrirCotizacion(motoDesdeApi(moto), tipo);
    }
  }

  protected numero(evento: Event): number {
    const valor = Number((evento.target as HTMLInputElement).value);
    return Number.isFinite(valor) ? valor : 0;
  }

  protected marcado(evento: Event): boolean {
    return (evento.target as HTMLInputElement).checked;
  }

  protected porcentaje(valor: number, total: number): number {
    return total > 0 ? (valor / total) * 100 : 0;
  }

  protected tasa(valor: number): string {
    return `${(valor * 100).toFixed(2).replace('.', ',')} %`;
  }

  private buscar(id: string): Observable<MotoDetalleApi> {
    if (/^\d+$/.test(id)) {
      return this.api.detalle(id);
    }
    const local = this.catalogo.porId(id);
    return this.api.listar().pipe(
      switchMap((motos) => {
        const igual = motos.find(
          (moto) => local && moto.modelo === local.modelo && moto.marca === local.marca,
        );
        if (!igual) {
          throw new Error('Moto no encontrada');
        }
        return this.api.detalle(igual.id);
      }),
    );
  }
}
