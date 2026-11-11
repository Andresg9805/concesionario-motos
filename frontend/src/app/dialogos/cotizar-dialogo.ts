import { Component, ElementRef, computed, effect, inject, signal, viewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AtencionService } from '../core/atencion.service';
import { cuotaMensual, licenciaPara } from '../core/finanzas';
import { MARCAS } from '../core/marcas';
import { Atencion, TipoAtencion } from '../core/modelos';
import { UiService } from '../core/ui.service';
import { CopPipe } from '../shared/cop.pipe';
import { Icono } from '../shared/icono';

const CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const CELULAR = /^3\d{9}$/;

@Component({
  selector: 'app-cotizar-dialogo',
  imports: [FormsModule, Icono, CopPipe],
  template: `
    <dialog
      #dialogo
      aria-labelledby="tituloCotizacion"
      class="theme-t m-auto"
      (close)="ui.cerrarCotizacion()"
    >
      @if (moto(); as moto) {
        <div
          class="sheet w-[min(560px,calc(100vw-32px))] overflow-hidden rounded-xl border border-line bg-surface shadow-2xl"
          [style.--mark]="marca()?.color"
        >
          <div class="flex items-start justify-between gap-4 border-b border-line p-5">
            <div class="min-w-0">
              <p class="eyebrow text-accenttext">{{ marca()?.nombre }}</p>
              <h2 id="tituloCotizacion" class="mt-1 font-display text-xl font-extrabold">
                {{ moto.modelo }}
              </h2>
              <p class="num mt-0.5 text-sm text-muted">
                {{ moto.cc }} cc · Licencia {{ licencia() }} · {{ moto.precio | cop }}
              </p>
            </div>
            <button
              type="button"
              class="grid h-9 w-9 shrink-0 place-items-center rounded-md hover:bg-surface2"
              aria-label="Cerrar"
              (click)="cerrar()"
            >
              <app-icono nombre="x" class="h-5 w-5" />
            </button>
          </div>

          @if (resultado(); as r) {
            <div class="flex flex-col gap-4 p-5" aria-live="polite">
              <div class="flex items-center gap-2 text-sm text-ok">
                <app-icono nombre="check-circle-2" class="h-5 w-5" />{{
                  r.tipo === 'testdrive'
                    ? 'Test drive en la cola del asesor'
                    : 'Cotización registrada'
                }}
              </div>
              <div class="rounded-lg border border-line bg-surface2 p-4">
                <p class="text-xs text-muted">Tu código de seguimiento</p>
                <div class="mt-1 flex items-center justify-between gap-3">
                  <span class="font-mono text-3xl font-semibold tracking-widest select-all">{{
                    r.codigo
                  }}</span>
                  <button
                    type="button"
                    class="inline-flex h-9 items-center gap-1.5 rounded-md border border-line bg-surface px-3 text-sm font-medium hover:bg-bg"
                    (click)="copiar(r.codigo)"
                  >
                    <app-icono [nombre]="copiado() ? 'check' : 'copy'" class="h-4 w-4" />{{
                      copiado() ? 'Copiado' : 'Copiar'
                    }}
                  </button>
                </div>
                <p class="mt-1 text-xs text-muted">
                  Estado inicial: <span class="font-mono">{{ r.estado }}</span>
                </p>
              </div>
              <dl class="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <dt class="text-xs text-muted">Asesor {{ marca()?.nombre }}</dt>
                  <dd class="font-bold">{{ r.asesor.nombre }}</dd>
                </div>
                <div>
                  <dt class="text-xs text-muted">WhatsApp del asesor</dt>
                  <dd class="font-mono select-all">{{ r.asesor.whatsapp }}</dd>
                </div>
                <div>
                  <dt class="text-xs text-muted">Moto</dt>
                  <dd>{{ moto.modelo }} · {{ licencia() }}</dd>
                </div>
                <div>
                  <dt class="text-xs text-muted">Cuota estimada</dt>
                  <dd class="num font-mono">{{ cuota() | cop }} × {{ plazo() }}</dd>
                </div>
              </dl>
              <p class="text-xs text-muted">
                El asesor te escribirá por WhatsApp. Guarda el código para consultar el estado sin
                crear cuenta.
              </p>
              <div class="flex flex-wrap gap-2">
                <button
                  type="button"
                  class="cta inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-bold"
                  (click)="verSeguimiento(r.codigo)"
                >
                  Ver seguimiento
                </button>
                <button
                  type="button"
                  class="inline-flex h-10 items-center rounded-md border border-line px-4 text-sm font-medium hover:bg-surface2"
                  (click)="cerrar()"
                >
                  Cerrar
                </button>
              </div>
            </div>
          } @else {
            <form
              class="flex max-h-[70dvh] flex-col gap-4 overflow-y-auto p-5"
              novalidate
              (ngSubmit)="enviar()"
            >
              <fieldset>
                <legend class="text-sm font-medium">Quiero</legend>
                <div class="mt-1.5 grid grid-cols-2 gap-2">
                  <label
                    class="flex h-11 cursor-pointer items-center gap-2 rounded-md border border-line px-3 text-sm has-[:checked]:border-accent has-[:checked]:bg-accentsoft"
                    ><input
                      type="radio"
                      name="tipo"
                      value="cotizacion"
                      [ngModel]="tipo()"
                      (ngModelChange)="tipo.set($event)"
                    />
                    Cotización</label
                  >
                  <label
                    class="flex h-11 cursor-pointer items-center gap-2 rounded-md border border-line px-3 text-sm has-[:checked]:border-accent has-[:checked]:bg-accentsoft"
                    ><input
                      type="radio"
                      name="tipo"
                      value="testdrive"
                      [ngModel]="tipo()"
                      (ngModelChange)="tipo.set($event)"
                    />
                    Test drive</label
                  >
                </div>
              </fieldset>
              <div class="grid gap-4 sm:grid-cols-2">
                <label class="text-sm font-medium" for="qInicial"
                  >Cuota inicial: <span class="num font-bold">{{ inicialPct() }} %</span>
                  <input
                    id="qInicial"
                    name="inicial"
                    type="range"
                    min="0"
                    max="50"
                    step="5"
                    class="mt-3 w-full"
                    [ngModel]="inicialPct()"
                    (ngModelChange)="inicialPct.set(+$event)"
                  />
                </label>
                <label class="text-sm font-medium" for="qPlazo"
                  >Plazo
                  <select
                    id="qPlazo"
                    name="plazo"
                    class="field mt-1 h-11 w-full rounded-md px-3"
                    [ngModel]="plazo()"
                    (ngModelChange)="plazo.set(+$event)"
                  >
                    @for (meses of plazos; track meses) {
                      <option [ngValue]="meses">{{ meses }} meses</option>
                    }
                  </select>
                </label>
              </div>
              <div class="flex items-baseline justify-between rounded-md bg-accentsoft px-4 py-3">
                <span class="text-sm">Cuota mensual estimada</span>
                <span class="num font-mono text-lg font-semibold text-accenttext">{{
                  cuota() | cop
                }}</span>
              </div>
              @if (tipo() === 'testdrive' && licencia() === 'A2') {
                <div
                  class="flex items-start gap-2 rounded-md border border-line px-3 py-2 text-xs text-muted"
                >
                  <app-icono nombre="id-card" class="mt-0.5 h-4 w-4" /><span
                    >Para el test drive de esta moto necesitas licencia A2.</span
                  >
                </div>
              }
              <div class="grid gap-4 sm:grid-cols-2">
                <label class="text-sm font-medium sm:col-span-2" for="qNombre"
                  >Nombre completo
                  <input
                    id="qNombre"
                    name="nombre"
                    autocomplete="name"
                    class="field mt-1 h-11 w-full rounded-md px-3"
                    [attr.aria-invalid]="!!errores()['nombre']"
                    [(ngModel)]="nombre"
                  />
                  @if (errores()['nombre']) {
                    <span class="mt-1 block text-xs text-danger">{{ errores()['nombre'] }}</span>
                  }
                </label>
                <label class="text-sm font-medium" for="qCorreo"
                  >Correo
                  <input
                    id="qCorreo"
                    name="correo"
                    type="email"
                    autocomplete="email"
                    class="field mt-1 h-11 w-full rounded-md px-3"
                    [attr.aria-invalid]="!!errores()['correo']"
                    [(ngModel)]="correo"
                  />
                  @if (errores()['correo']) {
                    <span class="mt-1 block text-xs text-danger">{{ errores()['correo'] }}</span>
                  }
                </label>
                <label class="text-sm font-medium" for="qCelular"
                  >Celular
                  <input
                    id="qCelular"
                    name="celular"
                    type="tel"
                    inputmode="numeric"
                    maxlength="10"
                    class="field num mt-1 h-11 w-full rounded-md px-3"
                    placeholder="3001234567"
                    [attr.aria-invalid]="!!errores()['celular']"
                    [(ngModel)]="celular"
                  />
                  @if (errores()['celular']) {
                    <span class="mt-1 block text-xs text-danger">{{ errores()['celular'] }}</span>
                  }
                </label>
              </div>
              <label class="flex items-start gap-2 text-xs text-muted" for="qTerminos">
                <input
                  id="qTerminos"
                  name="terminos"
                  type="checkbox"
                  class="mt-0.5 h-4 w-4"
                  [(ngModel)]="terminos"
                />
                <span
                  >Autorizo que un asesor me contacte por WhatsApp y el tratamiento de mis datos
                  según la Ley 1581 de 2012.</span
                >
              </label>
              @if (errores()['terminos']) {
                <span class="-mt-3 text-xs text-danger">{{ errores()['terminos'] }}</span>
              }
              <button
                type="submit"
                class="cta inline-flex h-11 items-center justify-center gap-2 rounded-md text-sm font-bold"
              >
                <app-icono nombre="send" class="h-4 w-4" /><span>{{
                  tipo() === 'testdrive' ? 'Pedir test drive' : 'Solicitar cotización'
                }}</span>
              </button>
            </form>
          }
        </div>
      }
    </dialog>
  `,
})
export class CotizarDialogo {
  protected readonly ui = inject(UiService);
  private readonly atencion = inject(AtencionService);
  private readonly dialogo = viewChild.required<ElementRef<HTMLDialogElement>>('dialogo');

  protected readonly plazos = [12, 24, 36, 48, 60];
  protected readonly moto = computed(() => this.ui.cotizacion()?.moto ?? null);
  protected readonly marca = computed(() => {
    const moto = this.moto();
    return moto ? MARCAS[moto.marca] : null;
  });
  protected readonly licencia = computed(() => licenciaPara(this.moto()?.cc ?? 0));
  protected readonly tipo = signal<TipoAtencion>('cotizacion');
  protected readonly inicialPct = signal(10);
  protected readonly plazo = signal(36);
  protected readonly cuota = computed(() =>
    cuotaMensual(this.moto()?.precio ?? 0, this.inicialPct(), this.plazo()),
  );
  protected readonly errores = signal<Record<string, string>>({});
  protected readonly resultado = signal<Atencion | null>(null);
  protected readonly copiado = signal(false);

  protected nombre = '';
  protected correo = '';
  protected celular = '';
  protected terminos = false;

  constructor() {
    effect(() => {
      const solicitud = this.ui.cotizacion();
      const dialogo = this.dialogo().nativeElement;
      if (solicitud) {
        this.tipo.set(solicitud.tipo);
        this.resultado.set(null);
        this.errores.set({});
        this.copiado.set(false);
        if (!dialogo.open) {
          dialogo.showModal?.();
        }
      } else if (dialogo.open) {
        dialogo.close();
      }
    });
  }

  protected enviar(): void {
    const moto = this.moto();
    if (!moto) {
      return;
    }
    const errores: Record<string, string> = {};
    if (this.nombre.trim().length < 3) {
      errores['nombre'] = 'Escribe tu nombre.';
    }
    if (!CORREO.test(this.correo.trim())) {
      errores['correo'] = 'Escribe un correo válido.';
    }
    if (!CELULAR.test(this.celular.trim())) {
      errores['celular'] = 'El celular tiene 10 dígitos y empieza por 3.';
    }
    if (!this.terminos) {
      errores['terminos'] = 'Necesitamos tu autorización para que el asesor te contacte.';
    }
    this.errores.set(errores);
    if (Object.keys(errores).length > 0) {
      return;
    }
    this.resultado.set(this.atencion.registrar(moto, this.tipo()));
  }

  protected copiar(codigo: string): void {
    navigator.clipboard?.writeText(codigo).then(
      () => this.copiado.set(true),
      () => this.copiado.set(false),
    );
  }

  protected verSeguimiento(codigo: string): void {
    this.cerrar();
    this.ui.codigoBuscado.set(codigo);
  }

  protected cerrar(): void {
    this.ui.cerrarCotizacion();
  }
}
