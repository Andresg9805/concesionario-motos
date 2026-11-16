import { Component, inject, signal } from '@angular/core';
import { SesionService } from '../../core/sesion.service';
import { Icono } from '../../shared/icono';
import { AdminAccesorios } from './admin-accesorios';
import { AdminMotos } from './admin-motos';
import { AdminParametros } from './admin-parametros';
import { AdminPedidos } from './admin-pedidos';
import { AdminReportes } from './admin-reportes';

type Pestana = 'pedidos' | 'motos' | 'accesorios' | 'parametros' | 'reportes';

const PESTANAS: readonly { clave: Pestana; nombre: string; icono: string }[] = [
  { clave: 'pedidos', nombre: 'Pedidos y envíos', icono: 'shopping-bag' },
  { clave: 'motos', nombre: 'Motos', icono: 'flag' },
  { clave: 'accesorios', nombre: 'Accesorios', icono: 'shield' },
  { clave: 'parametros', nombre: 'Parámetros de costo', icono: 'wallet' },
  { clave: 'reportes', nombre: 'Reportes', icono: 'chart-column' },
];

@Component({
  selector: 'app-panel-admin',
  imports: [AdminAccesorios, AdminMotos, AdminParametros, AdminPedidos, AdminReportes, Icono],
  template: `
    <section class="relative overflow-hidden border-b border-line bg-surface2">
      <div class="resplandor pointer-events-none absolute inset-0" aria-hidden="true"></div>
      <div class="gutter relative mx-auto max-w-7xl py-10">
        <p class="eyebrow text-muted">Administración</p>
        <h1 class="mt-2 font-display text-3xl font-extrabold md:text-[42px]">
          Hola, {{ primerNombre }}
        </h1>
        <p class="mt-2 max-w-xl text-sm text-muted">
          Despacha los pedidos de la tienda, mantén el catálogo al día, ajusta los valores con los
          que se calcula el costo real de cada moto y revisa los reportes.
        </p>
        @if (porDespachar() > 0) {
          <p
            class="mt-4 inline-flex items-center gap-2 rounded-full bg-accent px-3 py-1 text-xs font-bold text-onaccent"
          >
            <app-icono nombre="clock" class="h-3.5 w-3.5" />
            {{ porDespachar() }} {{ porDespachar() === 1 ? 'pedido' : 'pedidos' }} por despachar
          </p>
        }
      </div>
    </section>

    <div class="gutter mx-auto max-w-7xl py-8">
      <div role="tablist" aria-label="Secciones de administración" class="flex flex-wrap gap-2">
        @for (p of pestanas; track p.clave) {
          <button
            type="button"
            role="tab"
            class="tab inline-flex h-10 items-center gap-2 rounded-md border border-line px-4 text-sm font-bold"
            [attr.aria-selected]="pestana() === p.clave"
            (click)="pestana.set(p.clave)"
          >
            <app-icono [nombre]="p.icono" class="h-4 w-4" /> {{ p.nombre }}
          </button>
        }
      </div>

      <div class="mt-6">
        @switch (pestana()) {
          @case ('pedidos') {
            <app-admin-pedidos (porDespachar)="porDespachar.set($event)" />
          }
          @case ('motos') {
            <app-admin-motos />
          }
          @case ('accesorios') {
            <app-admin-accesorios />
          }
          @case ('parametros') {
            <app-admin-parametros />
          }
          @case ('reportes') {
            <app-admin-reportes />
          }
        }
      </div>
    </div>
  `,
})
export class PanelAdmin {
  private readonly sesion = inject(SesionService);

  protected readonly pestanas = PESTANAS;
  protected readonly pestana = signal<Pestana>('pedidos');
  protected readonly porDespachar = signal(0);
  protected readonly primerNombre = this.sesion.usuario()?.nombre.split(' ')[0] ?? '';
}
