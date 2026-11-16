import { Component, computed, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';
import {
  AsesorApiService,
  AtencionAsesorApi,
  ETAPAS,
  EstadoCotizacion,
  GrupoCotizacion,
  NOMBRE_ESTADO,
  enlaceWhatsapp,
  fechaLocal,
  grupoDe,
  mensajeCliente,
  mensajeError,
  siguientesEstados,
} from '../../core/asesor-api';
import { MARCAS } from '../../core/marcas';
import { SesionService } from '../../core/sesion.service';
import { UiService } from '../../core/ui.service';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';

type Pestana = 'cotizaciones' | 'testdrives';
type Carga = 'cargando' | 'error' | 'listo';

const ACCION: Record<EstadoCotizacion, string> = {
  NUEVO: 'Nuevo',
  CONTACTADO: 'Ya lo contacté',
  TEST_DRIVE: 'Agendó test drive',
  NEGOCIANDO: 'En negociación',
  VENDIDO: 'Moto vendida',
  DESCARTADO: 'Descartar',
};

const GRUPOS: readonly { clave: GrupoCotizacion; nombre: string }[] = [
  { clave: 'abiertas', nombre: 'Abiertas' },
  { clave: 'vendidas', nombre: 'Vendidas' },
  { clave: 'descartadas', nombre: 'Descartadas' },
];

const FORMATO_FECHA = new Intl.DateTimeFormat('es-CO', {
  day: 'numeric',
  month: 'short',
  hour: 'numeric',
  minute: '2-digit',
});

function mananaDiezAm(): string {
  const fecha = new Date();
  fecha.setDate(fecha.getDate() + 1);
  fecha.setHours(10, 0, 0, 0);
  return fechaLocal(fecha);
}

@Component({
  selector: 'app-panel-asesor',
  imports: [CopPipe, Icono],
  template: `
    <section class="relative overflow-hidden border-b border-line bg-surface2">
      <div class="resplandor pointer-events-none absolute inset-0" aria-hidden="true"></div>
      <div
        class="seigaiha pointer-events-none absolute top-0 -right-10 h-40 w-80 opacity-60"
        aria-hidden="true"
      ></div>
      <div class="gutter relative mx-auto max-w-7xl py-10">
        <p class="eyebrow eyebrow-marca text-muted">{{ subtitulo() }}</p>
        <h1 class="mt-2 font-display text-3xl font-extrabold md:text-[42px]">
          Hola, {{ primerNombre() }}
        </h1>
        <p class="mt-2 max-w-xl text-sm text-muted">
          Aquí ves las cotizaciones que te asignaron y la cola de test drives de tu marca.
        </p>
        <dl class="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
          <div class="rounded-lg border border-line bg-surface p-4">
            <dt class="text-xs text-muted">Sin contactar</dt>
            <dd class="num mt-1 font-display text-2xl font-extrabold">{{ resumen().nuevas }}</dd>
          </div>
          <div class="rounded-lg border border-line bg-surface p-4">
            <dt class="text-xs text-muted">Cotizaciones abiertas</dt>
            <dd class="num mt-1 font-display text-2xl font-extrabold">{{ resumen().abiertas }}</dd>
          </div>
          <div class="rounded-lg border border-line bg-surface p-4">
            <dt class="text-xs text-muted">Motos vendidas</dt>
            <dd class="num mt-1 font-display text-2xl font-extrabold">{{ resumen().vendidas }}</dd>
          </div>
          <div class="rounded-lg border border-line bg-surface p-4">
            <dt class="text-xs text-muted">Test drives en cola</dt>
            <dd class="num mt-1 font-display text-2xl font-extrabold">{{ cola().length }}</dd>
          </div>
        </dl>
      </div>
    </section>

    <div class="gutter mx-auto max-w-7xl py-8">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div role="tablist" aria-label="Secciones del panel" class="flex gap-2">
          <button
            type="button"
            role="tab"
            class="tab inline-flex h-10 items-center gap-2 rounded-md border border-line px-4 text-sm font-bold"
            [attr.aria-selected]="pestana() === 'cotizaciones'"
            (click)="pestana.set('cotizaciones')"
          >
            <app-icono nombre="file-text" class="h-4 w-4" /> Mis cotizaciones
            <span class="num opacity-80">{{ cotizaciones().length }}</span>
          </button>
          <button
            type="button"
            role="tab"
            class="tab inline-flex h-10 items-center gap-2 rounded-md border border-line px-4 text-sm font-bold"
            [attr.aria-selected]="pestana() === 'testdrives'"
            (click)="pestana.set('testdrives')"
          >
            <app-icono nombre="flag" class="h-4 w-4" /> Test drives
            <span class="num opacity-80">{{ cola().length }}</span>
          </button>
        </div>
        <button
          type="button"
          class="inline-flex h-10 items-center gap-2 rounded-md border border-line px-3 text-sm text-muted hover:text-fg"
          [disabled]="carga() === 'cargando'"
          (click)="cargar()"
        >
          <app-icono nombre="refresh-cw" class="h-4 w-4" /> Actualizar
        </button>
      </div>

      @switch (carga()) {
        @case ('cargando') {
          <div class="mt-6 grid gap-3" aria-busy="true">
            @for (i of [1, 2, 3]; track i) {
              <div class="h-28 animate-pulse rounded-lg bg-surface2"></div>
            }
          </div>
        }
        @case ('error') {
          <div class="mt-6 rounded-lg border border-line bg-surface p-6 text-center" role="alert">
            <p class="font-bold">No pudimos cargar tu panel</p>
            <p class="mt-1 text-sm text-muted">
              Revisa que el servidor esté encendido y vuelve a intentarlo.
            </p>
            <button
              type="button"
              class="cta mt-4 inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-bold"
              (click)="cargar()"
            >
              <app-icono nombre="refresh-cw" class="h-4 w-4" /> Reintentar
            </button>
          </div>
        }
        @case ('listo') {
          @if (pestana() === 'cotizaciones') {
            <div class="mt-6 flex flex-wrap gap-2" aria-label="Filtrar cotizaciones">
              @for (g of grupos; track g.clave) {
                <button
                  type="button"
                  class="chip inline-flex h-9 items-center gap-2 rounded-full border border-line px-4 text-sm"
                  [attr.aria-pressed]="grupo() === g.clave"
                  (click)="grupo.set(g.clave)"
                >
                  {{ g.nombre }} <span class="num font-bold">{{ conteo()[g.clave] }}</span>
                </button>
              }
            </div>

            @if (filtradas().length === 0) {
              <p
                class="mt-6 rounded-lg border border-dashed border-line p-8 text-center text-sm text-muted"
              >
                No tienes cotizaciones {{ grupo() }} por ahora.
              </p>
            } @else {
              <ul class="mt-6 grid gap-4 lg:grid-cols-2">
                @for (c of filtradas(); track c.id) {
                  <li class="flex flex-col rounded-lg border border-line bg-surface p-5">
                    <div class="flex items-start justify-between gap-3">
                      <div>
                        <p class="num font-mono text-xs text-muted">
                          {{ c.codigo }} · {{ fecha(c.creada_en) }}
                        </p>
                        <h2 class="mt-1 font-display text-xl font-extrabold">
                          {{ c.moto.marca.nombre }} {{ c.moto.modelo }}
                        </h2>
                      </div>
                      <span
                        class="shrink-0 rounded-full px-3 py-1 text-xs font-bold"
                        [class]="claseEstado(c.estado)"
                        >{{ nombreEstado[c.estado] ?? c.estado }}</span
                      >
                    </div>

                    @if (c.estado !== 'DESCARTADO') {
                      <ol class="mt-4 flex gap-1" aria-label="Avance de la venta">
                        @for (etapa of etapas; track etapa; let i = $index) {
                          <li
                            class="h-1.5 flex-1 rounded-full"
                            [class.bg-accent]="i <= indiceEtapa(c.estado)"
                            [class.bg-surface2]="i > indiceEtapa(c.estado)"
                            [attr.title]="nombreEstado[etapa]"
                          ></li>
                        }
                      </ol>
                    }

                    <div class="mt-4 grid gap-1 text-sm">
                      <p class="flex items-center gap-2">
                        <app-icono nombre="user" class="h-4 w-4 text-muted" />
                        <span class="font-bold">{{ c.cliente.nombre }}</span>
                      </p>
                      <p class="text-muted">{{ c.cliente.celular }} · {{ c.cliente.correo }}</p>
                      @if (c.cuota_mensual_cop) {
                        <p>
                          Cuota estimada
                          <span class="num font-bold">{{ c.cuota_mensual_cop | cop }}</span> al mes
                        </p>
                      }
                    </div>

                    <div class="mt-5 flex flex-wrap items-center gap-2 border-t border-line pt-4">
                      <a
                        class="inline-flex h-9 items-center gap-2 rounded-md border border-line px-3 text-sm font-bold hover:border-accent"
                        target="_blank"
                        rel="noopener"
                        [href]="whatsapp(c)"
                      >
                        <app-icono nombre="send" class="h-4 w-4" /> WhatsApp
                      </a>
                      @for (siguiente of siguientes(c.estado); track siguiente) {
                        <button
                          type="button"
                          class="inline-flex h-9 items-center gap-2 rounded-md px-3 text-sm font-bold"
                          [class.cta]="siguiente !== 'DESCARTADO'"
                          [class.text-danger]="siguiente === 'DESCARTADO'"
                          [class.border]="siguiente === 'DESCARTADO'"
                          [class.border-line]="siguiente === 'DESCARTADO'"
                          [disabled]="ocupada() === c.id"
                          (click)="cambiar(c, siguiente)"
                        >
                          @if (siguiente === 'DESCARTADO') {
                            <app-icono nombre="x" class="h-4 w-4" />
                          } @else {
                            <app-icono nombre="check" class="h-4 w-4" />
                          }
                          {{ accion[siguiente] }}
                        </button>
                      }
                    </div>
                  </li>
                }
              </ul>
            }
          } @else {
            <div class="mt-6 grid gap-6 lg:grid-cols-[1.2fr_1fr]">
              <div>
                <h2 class="font-display text-xl font-extrabold">Siguiente en la cola</h2>
                <p class="mt-1 text-sm text-muted">
                  Se atienden en orden de llegada: primero el que lleva más tiempo esperando.
                </p>
                @if (primero(); as t) {
                  <div class="mt-4 rounded-lg border-2 border-accent bg-surface p-5">
                    <p class="num font-mono text-xs text-muted">
                      {{ t.codigo }} · solicitado {{ fecha(t.creada_en) }}
                    </p>
                    <h3 class="mt-1 font-display text-2xl font-extrabold">
                      {{ t.moto.marca.nombre }} {{ t.moto.modelo }}
                    </h3>
                    <p class="mt-3 flex items-center gap-2 text-sm">
                      <app-icono nombre="user" class="h-4 w-4 text-muted" />
                      <span class="font-bold">{{ t.cliente.nombre }}</span>
                    </p>
                    <p class="text-sm text-muted">
                      {{ t.cliente.celular }} · {{ t.cliente.correo }}
                    </p>
                    <div
                      class="mt-5 grid gap-3 border-t border-line pt-4 sm:grid-cols-[1fr_auto] sm:items-end"
                    >
                      <label class="grid gap-1 text-sm">
                        <span class="font-bold">Fecha y hora del test drive</span>
                        <input
                          type="datetime-local"
                          class="field h-10 rounded-md px-3"
                          [min]="minimo"
                          [value]="fechaPrueba()"
                          (input)="fechaPrueba.set($any($event.target).value)"
                        />
                      </label>
                      <button
                        type="button"
                        class="cta inline-flex h-10 items-center justify-center gap-2 rounded-md px-4 text-sm font-bold"
                        [disabled]="programando() || !fechaPrueba()"
                        (click)="programar()"
                      >
                        <app-icono nombre="play" class="h-4 w-4" /> Programar
                      </button>
                    </div>
                    <a
                      class="mt-3 inline-flex items-center gap-2 text-sm font-bold text-accenttext hover:underline"
                      target="_blank"
                      rel="noopener"
                      [href]="whatsapp(t)"
                    >
                      <app-icono nombre="send" class="h-4 w-4" /> Escribirle por WhatsApp
                    </a>
                  </div>
                } @else {
                  <p
                    class="mt-4 rounded-lg border border-dashed border-line p-8 text-center text-sm text-muted"
                  >
                    No hay test drives esperando. Cuando un cliente pida uno, aparece aquí.
                  </p>
                }

                @if (enEspera().length > 0) {
                  <h3 class="mt-6 text-sm font-bold">Después siguen</h3>
                  <ol class="mt-2 grid gap-2">
                    @for (t of enEspera(); track t.id; let i = $index) {
                      <li
                        class="flex items-center gap-3 rounded-lg border border-line bg-surface p-3 text-sm"
                      >
                        <span
                          class="num grid h-7 w-7 shrink-0 place-items-center rounded-full bg-surface2 text-xs font-bold"
                          >{{ i + 2 }}</span
                        >
                        <div class="min-w-0 flex-1">
                          <p class="truncate font-bold">{{ t.cliente.nombre }}</p>
                          <p class="truncate text-muted">
                            {{ t.moto.marca.nombre }} {{ t.moto.modelo }} · {{ fecha(t.creada_en) }}
                          </p>
                        </div>
                      </li>
                    }
                  </ol>
                }
              </div>

              <div>
                <h2 class="font-display text-xl font-extrabold">Programados</h2>
                <p class="mt-1 text-sm text-muted">Los que agendaste en esta sesión.</p>
                @if (programados().length === 0) {
                  <p
                    class="mt-4 rounded-lg border border-dashed border-line p-8 text-center text-sm text-muted"
                  >
                    Todavía no has programado ninguno.
                  </p>
                } @else {
                  <ul class="mt-4 grid gap-2">
                    @for (t of programados(); track t.id) {
                      <li class="rounded-lg border border-line bg-surface p-4 text-sm">
                        <p class="flex items-center justify-between gap-2">
                          <span class="font-bold">{{ t.cliente.nombre }}</span>
                          <span class="rounded-full bg-ok/15 px-3 py-1 text-xs font-bold text-ok">
                            {{ t.fecha_programada ? fecha(t.fecha_programada) : '' }}
                          </span>
                        </p>
                        <p class="mt-1 text-muted">
                          {{ t.moto.marca.nombre }} {{ t.moto.modelo }} · {{ t.codigo }}
                        </p>
                      </li>
                    }
                  </ul>
                }
              </div>
            </div>
          }
        }
      }
    </div>
  `,
})
export class PanelAsesor {
  private readonly api = inject(AsesorApiService);
  private readonly ui = inject(UiService);
  protected readonly sesion = inject(SesionService);

  protected readonly grupos = GRUPOS;
  protected readonly etapas = ETAPAS;
  protected readonly nombreEstado = NOMBRE_ESTADO;
  protected readonly accion = ACCION;
  protected readonly siguientes = siguientesEstados;
  protected readonly minimo = fechaLocal(new Date());

  protected readonly pestana = signal<Pestana>('cotizaciones');
  protected readonly grupo = signal<GrupoCotizacion>('abiertas');
  protected readonly carga = signal<Carga>('cargando');
  protected readonly cotizaciones = signal<AtencionAsesorApi[]>([]);
  protected readonly cola = signal<AtencionAsesorApi[]>([]);
  protected readonly programados = signal<AtencionAsesorApi[]>([]);
  protected readonly ocupada = signal<number | null>(null);
  protected readonly programando = signal(false);
  protected readonly fechaPrueba = signal(mananaDiezAm());

  protected readonly primerNombre = computed(
    () => this.sesion.usuario()?.nombre.split(' ')[0] ?? '',
  );

  protected readonly subtitulo = computed(() => {
    const marca = this.sesion.usuario()?.marca;
    return marca ? `Asesor · ${MARCAS[marca].nombre}` : 'Asesor';
  });

  protected readonly conteo = computed(() => {
    const conteo: Record<GrupoCotizacion, number> = { abiertas: 0, vendidas: 0, descartadas: 0 };
    for (const c of this.cotizaciones()) {
      conteo[grupoDe(c.estado)]++;
    }
    return conteo;
  });

  protected readonly resumen = computed(() => ({
    nuevas: this.cotizaciones().filter((c) => c.estado === 'NUEVO').length,
    abiertas: this.conteo().abiertas,
    vendidas: this.conteo().vendidas,
  }));

  protected readonly filtradas = computed(() =>
    this.cotizaciones()
      .filter((c) => grupoDe(c.estado) === this.grupo())
      .sort((a, b) => b.creada_en.localeCompare(a.creada_en)),
  );

  protected readonly primero = computed(() => this.cola()[0] ?? null);
  protected readonly enEspera = computed(() => this.cola().slice(1));

  constructor() {
    this.cargar();
  }

  cargar(): void {
    this.carga.set('cargando');
    forkJoin({ cotizaciones: this.api.atenciones(), cola: this.api.colaTestDrives() }).subscribe({
      next: ({ cotizaciones, cola }) => {
        this.cotizaciones.set(cotizaciones);
        this.cola.set(cola);
        this.carga.set('listo');
      },
      error: () => this.carga.set('error'),
    });
  }

  cambiar(cotizacion: AtencionAsesorApi, estado: EstadoCotizacion): void {
    this.ocupada.set(cotizacion.id);
    this.api.cambiarEstado(cotizacion.id, estado).subscribe({
      next: (actualizada) => {
        this.cotizaciones.update((lista) =>
          lista.map((c) => (c.id === actualizada.id ? actualizada : c)),
        );
        this.ocupada.set(null);
        this.ui.avisar(
          `${actualizada.codigo} quedó en ${NOMBRE_ESTADO[actualizada.estado] ?? actualizada.estado}`,
          'ok',
        );
      },
      error: (error) => {
        this.ocupada.set(null);
        this.ui.avisar(mensajeError(error, 'No se pudo cambiar el estado'), 'error');
      },
    });
  }

  programar(): void {
    this.programando.set(true);
    this.api.programarSiguiente(this.fechaPrueba()).subscribe({
      next: (programado) => {
        this.cola.update((lista) => lista.filter((t) => t.id !== programado.id));
        this.programados.update((lista) => [programado, ...lista]);
        this.programando.set(false);
        this.ui.avisar(`Test drive de ${programado.cliente.nombre} programado`, 'ok');
      },
      error: (error) => {
        this.programando.set(false);
        this.ui.avisar(mensajeError(error, 'No se pudo programar el test drive'), 'error');
      },
    });
  }

  protected whatsapp(atencion: AtencionAsesorApi): string {
    const asesor = this.sesion.usuario()?.nombre ?? 'tu asesor';
    return enlaceWhatsapp(atencion.cliente.celular, mensajeCliente(atencion, asesor));
  }

  protected fecha(valor: string): string {
    return FORMATO_FECHA.format(new Date(valor));
  }

  protected indiceEtapa(estado: string): number {
    return ETAPAS.indexOf(estado as EstadoCotizacion);
  }

  protected claseEstado(estado: string): string {
    if (estado === 'VENDIDO') {
      return 'bg-ok/15 text-ok';
    }
    if (estado === 'DESCARTADO') {
      return 'bg-danger/15 text-danger';
    }
    return estado === 'NUEVO' ? 'bg-accent text-onaccent' : 'bg-surface2 text-fg';
  }
}
