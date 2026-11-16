import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AdminApiService, ParametrosApi, detalleDelError } from '../../core/admin-api';
import { UiService } from '../../core/ui.service';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';

interface Formulario extends Omit<ParametrosApi, 'tasa_mensual'> {
  tasa_mensual_porcentaje: number;
}

function aFormulario(parametros: ParametrosApi): Formulario {
  const { tasa_mensual, ...resto } = parametros;
  return {
    ...resto,
    tarifas_soat: parametros.tarifas_soat.map((tarifa) => ({ ...tarifa })),
    tasa_mensual_porcentaje: Math.round(tasa_mensual * 100_000) / 1000,
  };
}

function aParametros(formulario: Formulario): ParametrosApi {
  const { tasa_mensual_porcentaje, ...resto } = formulario;
  return { ...resto, tasa_mensual: tasa_mensual_porcentaje / 100 };
}

@Component({
  selector: 'app-admin-parametros',
  imports: [CopPipe, FormsModule, Icono],
  template: `
    @if (formulario(); as f) {
      <form class="grid gap-6 lg:grid-cols-2" novalidate (ngSubmit)="guardar()">
        <section class="rounded-lg border border-line bg-surface p-5">
          <h2 class="font-display text-xl font-extrabold">Costos de tener una moto</h2>
          <p class="mt-1 text-sm text-muted">
            Con estos valores se calcula el costo real mensual y la cuota de crédito que ve el
            cliente.
          </p>
          <div class="mt-4 grid gap-4 sm:grid-cols-2">
            <label class="grid gap-1 text-sm font-medium">
              Precio del galón (COP)
              <input
                class="field h-10 w-full min-w-0 rounded-md px-3"
                type="number"
                name="galon"
                [(ngModel)]="f.precio_galon_cop"
              />
            </label>
            <label class="grid gap-1 text-sm font-medium">
              Impuesto vehicular (% anual)
              <input
                class="field h-10 w-full min-w-0 rounded-md px-3"
                type="number"
                step="0.1"
                name="impuesto"
                [(ngModel)]="f.porcentaje_impuesto"
              />
            </label>
            <label class="grid gap-1 text-sm font-medium">
              Matrícula (COP)
              <input
                class="field h-10 w-full min-w-0 rounded-md px-3"
                type="number"
                name="matricula"
                [(ngModel)]="f.valor_matricula_cop"
              />
            </label>
            <label class="grid gap-1 text-sm font-medium">
              Trámites (COP)
              <input
                class="field h-10 w-full min-w-0 rounded-md px-3"
                type="number"
                name="tramites"
                [(ngModel)]="f.valor_tramites_cop"
              />
            </label>
            <label class="grid gap-1 text-sm font-medium sm:col-span-2">
              Tasa de interés del crédito (% mensual)
              <input
                class="field h-10 w-full min-w-0 rounded-md px-3"
                type="number"
                step="0.01"
                name="tasa"
                [(ngModel)]="f.tasa_mensual_porcentaje"
              />
            </label>
          </div>
        </section>

        <section class="rounded-lg border border-line bg-surface p-5">
          <div class="flex items-center justify-between gap-3">
            <h2 class="font-display text-xl font-extrabold">Tarifas del SOAT</h2>
            <button
              type="button"
              class="inline-flex h-9 items-center gap-2 rounded-md border border-line px-3 text-sm font-bold"
              (click)="agregarTarifa(f)"
            >
              <app-icono nombre="plus" class="h-4 w-4" /> Agregar rango
            </button>
          </div>
          <div class="mt-4 grid gap-2">
            <div class="grid grid-cols-[1fr_1fr_1.4fr_auto] gap-2 text-xs text-muted">
              <span>Desde (cc)</span><span>Hasta (cc)</span><span>Valor anual</span>
              <span class="w-9"></span>
            </div>
            @for (tarifa of f.tarifas_soat; track $index; let i = $index) {
              <div class="grid grid-cols-[1fr_1fr_1.4fr_auto] items-center gap-2">
                <input
                  class="field h-9 w-full min-w-0 rounded-md px-2"
                  type="number"
                  [name]="'min' + i"
                  [attr.aria-label]="'Desde, rango ' + (i + 1)"
                  [(ngModel)]="tarifa.cilindraje_min"
                />
                <input
                  class="field h-9 w-full min-w-0 rounded-md px-2"
                  type="number"
                  [name]="'max' + i"
                  [attr.aria-label]="'Hasta, rango ' + (i + 1)"
                  [(ngModel)]="tarifa.cilindraje_max"
                />
                <input
                  class="field h-9 w-full min-w-0 rounded-md px-2"
                  type="number"
                  [name]="'valor' + i"
                  [attr.aria-label]="'Valor anual, rango ' + (i + 1)"
                  [(ngModel)]="tarifa.valor_anual_cop"
                />
                <button
                  type="button"
                  class="grid h-9 w-9 place-items-center rounded-md border border-line text-danger"
                  [attr.aria-label]="'Quitar rango ' + (i + 1)"
                  [disabled]="f.tarifas_soat.length === 1"
                  (click)="f.tarifas_soat.splice(i, 1)"
                >
                  <app-icono nombre="x" class="h-4 w-4" />
                </button>
              </div>
            }
          </div>
          <p class="mt-3 text-xs text-muted">
            Ejemplo: una moto de 184 cc paga
            <span class="num font-bold">{{ soatPara(f, 184) | cop }}</span> al año.
          </p>
        </section>

        <div class="lg:col-span-2">
          <button
            type="submit"
            class="cta inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-bold"
            [disabled]="guardando()"
          >
            <app-icono nombre="check" class="h-4 w-4" /> Guardar parámetros
          </button>
        </div>
      </form>
    } @else {
      <div class="h-64 animate-pulse rounded-lg bg-surface2" aria-busy="true"></div>
    }
  `,
})
export class AdminParametros {
  private readonly api = inject(AdminApiService);
  private readonly ui = inject(UiService);

  protected readonly formulario = signal<Formulario | null>(null);
  protected readonly guardando = signal(false);

  constructor() {
    this.api.parametros().subscribe({
      next: (parametros) => this.formulario.set(aFormulario(parametros)),
      error: (error) =>
        this.ui.avisar(detalleDelError(error, 'No se pudieron cargar los parámetros'), 'error'),
    });
  }

  agregarTarifa(formulario: Formulario): void {
    const ultima = formulario.tarifas_soat[formulario.tarifas_soat.length - 1];
    const desde = ultima ? ultima.cilindraje_max + 1 : 0;
    formulario.tarifas_soat.push({
      cilindraje_min: desde,
      cilindraje_max: desde + 100,
      valor_anual_cop: ultima?.valor_anual_cop ?? 0,
    });
  }

  protected soatPara(formulario: Formulario, cilindraje: number): number {
    return (
      formulario.tarifas_soat.find(
        (t) => cilindraje >= t.cilindraje_min && cilindraje <= t.cilindraje_max,
      )?.valor_anual_cop ?? 0
    );
  }

  guardar(): void {
    const formulario = this.formulario();
    if (!formulario) {
      return;
    }
    this.guardando.set(true);
    this.api.guardarParametros(aParametros(formulario)).subscribe({
      next: (guardados) => {
        this.formulario.set(aFormulario(guardados));
        this.guardando.set(false);
        this.ui.avisar('Parámetros guardados', 'ok');
      },
      error: (error) => {
        this.guardando.set(false);
        this.ui.avisar(detalleDelError(error, 'No se pudieron guardar los parámetros'), 'error');
      },
    });
  }
}
