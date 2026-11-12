import { Component, computed, inject } from '@angular/core';
import { CatalogoService } from '../../../core/catalogo.service';
import { FiltrosService } from '../../../core/filtros.service';
import { MarcaService } from '../../../core/marca.service';
import { NOMBRE_TIPO, ORDEN_TIPOS, SILUETA_TIPO, USO_TIPO } from '../../../core/marcas';
import { Silueta, TipoMoto } from '../../../core/modelos';
import { CopPipe } from '../../../shared/cop.pipe';
import { Icono } from '../../../shared/icono';
import { SiluetaMoto } from '../../../shared/silueta-moto';

export interface ResumenTipo {
  tipo: TipoMoto;
  numero: string;
  nombre: string;
  uso: string;
  silueta: Silueta;
  cantidad: number;
  desde: number | null;
}

@Component({
  selector: 'app-estilos',
  imports: [SiluetaMoto, Icono, CopPipe],
  template: `
    <section id="estilos" class="gutter mx-auto max-w-7xl pt-14" aria-labelledby="tituloEstilos">
      <div class="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p class="eyebrow eyebrow-marca text-muted">Paso 2</p>
          <h2 id="tituloEstilos" class="mt-1 font-display text-2xl font-extrabold md:text-3xl">
            Encuentra tu estilo
          </h2>
          <p class="mt-1 max-w-xl text-sm text-muted">
            Cada tipo de moto está pensado para un uso distinto. Elige uno y el catálogo te muestra
            solo esas motos.
          </p>
        </div>
        @if (filtros.tipo() !== 'todos') {
          <button
            type="button"
            class="inline-flex items-center gap-1 text-sm font-medium text-muted hover:text-fg"
            (click)="filtros.tipo.set('todos')"
          >
            <app-icono nombre="x" class="h-4 w-4" /> Ver todos los estilos
          </button>
        }
      </div>

      <div
        class="mt-6 grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4"
        role="group"
        aria-label="Estilos"
      >
        @for (item of resumen(); track item.tipo) {
          <button
            type="button"
            class="estilo group flex h-full flex-col overflow-hidden rounded-lg border bg-surface text-left disabled:opacity-50"
            [class]="
              filtros.tipo() === item.tipo
                ? 'border-accent ring-1 ring-accent'
                : 'border-line hover:border-muted'
            "
            [attr.aria-pressed]="filtros.tipo() === item.tipo"
            [disabled]="item.cantidad === 0"
            (click)="elegir(item.tipo)"
          >
            <span
              class="relative block aspect-[12/7] bg-surface2 px-3 pt-7 text-fg sm:px-6 sm:pt-4"
            >
              <app-silueta-moto [tipo]="item.silueta" />
              <span class="num absolute top-2 left-3 text-xs font-bold text-muted sm:top-3">{{
                item.numero
              }}</span>
              <span
                class="conteo num absolute top-2 right-2 rounded sm:top-3 sm:right-3 bg-accentsoft px-2 py-0.5 text-[11px] font-bold text-accenttext"
                >{{ item.cantidad }} {{ item.cantidad === 1 ? 'modelo' : 'modelos' }}</span
              >
            </span>
            <span class="flex flex-1 flex-col gap-2 p-3 sm:p-4">
              <span class="font-display text-lg leading-tight font-extrabold sm:text-xl">{{
                item.nombre
              }}</span>
              <span class="hidden text-sm text-muted sm:block">{{ item.uso }}</span>
              <span
                class="mt-auto flex flex-col gap-2 pt-2 sm:flex-row sm:items-end sm:justify-between"
              >
                <span class="text-xs text-muted">
                  @if (item.desde !== null) {
                    Desde
                    <span class="num block text-base font-bold text-fg">{{
                      item.desde | cop
                    }}</span>
                  } @else {
                    Sin modelos de esta marca
                  }
                </span>
                <span
                  class="inline-flex items-center gap-1 text-sm font-bold text-accenttext group-disabled:hidden"
                  >Ver motos <app-icono nombre="arrow-down" class="h-4 w-4"
                /></span>
              </span>
            </span>
          </button>
        }
      </div>
    </section>
  `,
})
export class Estilos {
  protected readonly filtros = inject(FiltrosService);
  private readonly catalogo = inject(CatalogoService);
  private readonly marcaService = inject(MarcaService);

  protected readonly resumen = computed<ResumenTipo[]>(() => {
    const motos = this.catalogo.porMarca(this.marcaService.actual());
    return ORDEN_TIPOS.map((tipo, i) => {
      const precios = motos.filter((moto) => moto.tipo === tipo).map((moto) => moto.precio);
      return {
        tipo,
        numero: String(i + 1).padStart(2, '0'),
        nombre: NOMBRE_TIPO[tipo],
        uso: USO_TIPO[tipo],
        silueta: SILUETA_TIPO[tipo],
        cantidad: precios.length,
        desde: precios.length ? Math.min(...precios) : null,
      };
    });
  });

  protected elegir(tipo: TipoMoto): void {
    this.filtros.tipo.set(tipo);
    const reducir =
      typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
    document.getElementById('catalogo')?.scrollIntoView({ behavior: reducir ? 'auto' : 'smooth' });
  }
}
