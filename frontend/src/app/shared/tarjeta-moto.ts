import { Component, computed, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { cuotaMensual, licenciaPara } from '../core/finanzas';
import { MARCAS, NOMBRE_TIPO, SILUETA_TIPO } from '../core/marcas';
import { Moto } from '../core/modelos';
import { UiService } from '../core/ui.service';
import { CopPipe } from './cop.pipe';
import { Icono } from './icono';
import { SiluetaMoto } from './silueta-moto';

@Component({
  selector: 'app-tarjeta-moto',
  imports: [SiluetaMoto, Icono, CopPipe, RouterLink],
  host: { class: 'block' },
  template: `
    <article
      class="flex h-full flex-col overflow-hidden rounded-lg border"
      [class]="marco()"
      [style.--mark]="marca().color"
    >
      <div
        class="relative aspect-[12/7] max-w-full px-6 pt-4"
        [class]="
          banda()
            ? 'bg-[color-mix(in_srgb,var(--on-band)_7%,transparent)] text-onband'
            : 'bg-surface2 text-fg'
        "
      >
        <app-silueta-moto [tipo]="silueta()" />
        <span
          class="absolute top-3 left-3 rounded px-2 py-0.5 text-[11px] font-bold"
          [class]="
            destacada()
              ? 'cta'
              : banda()
                ? 'bg-bandline text-onband'
                : 'bg-accentsoft text-accenttext'
          "
          >{{ tipo() }}</span
        >
        @if (destacada()) {
          <span
            class="absolute top-3 right-3 font-display text-[11px] font-extrabold"
            [class]="atenuado()"
            >推奨 · Recomendada</span
          >
        }
      </div>
      <div class="flex flex-1 flex-col gap-3 p-4">
        <div>
          <p class="flex items-center gap-1.5 text-xs" [class]="atenuado()">
            <span class="h-2 w-2 rounded-full" [style.background]="marca().color"></span
            >{{ marca().nombre }}
          </p>
          <h4 class="mt-0.5 font-display text-lg leading-snug font-extrabold">
            <a [routerLink]="['/motos', moto().id]" class="hover:underline">{{ moto().modelo }}</a>
          </h4>
        </div>
        <dl class="grid grid-cols-2 gap-x-3 gap-y-2 text-sm">
          <div>
            <dt class="text-xs" [class]="atenuado()">Cilindraje</dt>
            <dd class="num font-medium">{{ moto().cc }} cc</dd>
          </div>
          <div>
            <dt class="text-xs" [class]="atenuado()">Licencia</dt>
            <dd>
              <span
                class="inline-flex items-center gap-1 rounded border px-1.5 font-mono text-xs font-semibold"
                [class]="banda() ? 'border-bandline' : 'border-line'"
                [attr.title]="licencia() === 'A1' ? 'Hasta 125 cc' : 'Más de 125 cc'"
                ><app-icono nombre="id-card" class="h-3 w-3" />{{ licencia() }}</span
              >
            </dd>
          </div>
          <div>
            <dt class="text-xs" [class]="atenuado()">Precio de referencia</dt>
            <dd class="num font-mono text-[13px] font-semibold">{{ moto().precio | cop }}</dd>
          </div>
          <div>
            <dt class="text-xs" [class]="atenuado()">Cuota estimada</dt>
            <dd class="num font-mono text-[13px] font-semibold">
              {{ cuota() | cop
              }}<span class="font-sans text-xs font-normal" [class]="atenuado()">/mes</span>
            </dd>
          </div>
        </dl>
        <a
          [routerLink]="['/motos', moto().id]"
          class="inline-flex items-center gap-1 text-sm font-bold text-accenttext hover:underline"
          >Ver costo real <app-icono nombre="arrow-right" class="h-4 w-4"
        /></a>
        <div class="mt-auto grid grid-cols-2 gap-2">
          <button
            type="button"
            class="cta inline-flex h-10 items-center justify-center gap-2 rounded-md text-sm font-bold"
            (click)="ui.abrirCotizacion(moto(), 'cotizacion')"
          >
            <app-icono nombre="file-text" class="h-4 w-4" />Cotizar
          </button>
          <button
            type="button"
            class="inline-flex h-10 items-center justify-center gap-2 rounded-md border text-sm font-bold"
            [class]="
              banda()
                ? 'border-bandline hover:bg-[color-mix(in_srgb,var(--on-band)_8%,transparent)]'
                : 'border-line hover:bg-surface2'
            "
            (click)="ui.abrirCotizacion(moto(), 'testdrive')"
          >
            <app-icono nombre="flag" class="h-4 w-4" />Test drive
          </button>
        </div>
      </div>
    </article>
  `,
})
export class TarjetaMoto {
  protected readonly ui = inject(UiService);

  readonly moto = input.required<Moto>();
  readonly banda = input(false);
  readonly destacada = input(false);

  protected readonly marca = computed(() => MARCAS[this.moto().marca]);
  protected readonly licencia = computed(() => licenciaPara(this.moto().cc));
  protected readonly cuota = computed(() => cuotaMensual(this.moto().precio));
  protected readonly tipo = computed(() => NOMBRE_TIPO[this.moto().tipo]);
  protected readonly silueta = computed(() => SILUETA_TIPO[this.moto().tipo]);
  protected readonly marco = computed(() => {
    const fondo = this.banda()
      ? 'bg-[color-mix(in_srgb,var(--on-band)_4%,transparent)]'
      : 'bg-surface';
    if (this.destacada()) {
      return `${fondo} border-accent ring-1 ring-[var(--accent)]`;
    }
    return `${fondo} ${this.banda() ? 'border-bandline' : 'border-line'}`;
  });
  protected readonly atenuado = computed(() => (this.banda() ? 'text-bandmuted' : 'text-muted'));
}
