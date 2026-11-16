import { DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { textoCategoria } from '../../core/accesorios-api';
import {
  AdminApiService,
  RadarDemandaApi,
  ReporteVentasApi,
  demandaSinAtender,
  detalleDelError,
} from '../../core/admin-api';
import { UiService } from '../../core/ui.service';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';

@Component({
  selector: 'app-admin-reportes',
  imports: [CopPipe, DatePipe, Icono],
  template: `
    <div class="grid gap-6">
      <section class="rounded-lg border border-line bg-surface p-5">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 class="font-display text-xl font-extrabold">Radar de demanda</h2>
            <p class="mt-1 max-w-2xl text-sm text-muted">
              Lo que la gente busca por cuota frente a las motos que hay en stock. Una fila marcada
              es demanda que no estamos atendiendo.
            </p>
          </div>
          <button
            type="button"
            class="inline-flex h-9 items-center gap-2 rounded-md border border-line px-3 text-sm font-bold"
            (click)="cargar()"
          >
            <app-icono nombre="refresh-cw" class="h-4 w-4" /> Actualizar
          </button>
        </div>

        @if (radar(); as r) {
          @if (r.filas.length === 0) {
            <p class="mt-4 rounded-md border border-dashed border-line p-4 text-sm text-muted">
              Todavía no hay búsquedas por cuota.
            </p>
          } @else {
            <p class="mt-4 text-sm">
              <span class="num font-bold">{{ r.total_busquedas }}</span> búsquedas registradas
            </p>
            <div class="mt-3 overflow-x-auto">
              <table class="w-full min-w-[640px] text-left text-sm">
                <thead class="text-xs text-muted">
                  <tr class="border-b border-line">
                    <th class="py-2 pr-3 font-medium">Cuota que buscan</th>
                    <th class="py-2 pr-3 font-medium">Licencia</th>
                    <th class="py-2 pr-3 text-right font-medium">Búsquedas</th>
                    <th class="py-2 pr-3 text-right font-medium">Sin resultados</th>
                    <th class="py-2 pr-3 text-right font-medium">Resultados promedio</th>
                    <th class="py-2 text-right font-medium">Motos en stock</th>
                  </tr>
                </thead>
                <tbody>
                  @for (fila of r.filas; track fila.rango + fila.licencia) {
                    <tr
                      class="border-b border-line last:border-0"
                      [class.bg-accentsoft]="sinAtender(fila)"
                    >
                      <td class="py-2 pr-3 font-medium">
                        @if (sinAtender(fila)) {
                          <app-icono
                            nombre="alert-circle"
                            class="mr-1 h-4 w-4 align-[-3px] text-accent"
                          />
                        }
                        {{ fila.rango }}
                      </td>
                      <td class="py-2 pr-3">{{ fila.licencia }}</td>
                      <td class="num py-2 pr-3 text-right">{{ fila.busquedas }}</td>
                      <td class="num py-2 pr-3 text-right">{{ fila.sin_resultados }}</td>
                      <td class="num py-2 pr-3 text-right">{{ fila.promedio_resultados }}</td>
                      <td class="num py-2 text-right font-bold">{{ fila.motos_en_stock }}</td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          }
        } @else {
          <div class="mt-4 h-32 animate-pulse rounded-md bg-surface2" aria-busy="true"></div>
        }
      </section>

      <section class="rounded-lg border border-line bg-surface p-5">
        <h2 class="font-display text-xl font-extrabold">Ventas de accesorios</h2>
        <p class="mt-1 text-sm text-muted">Solo cuenta los pedidos pagados.</p>

        @if (ventas(); as v) {
          <div class="mt-4 grid gap-3 sm:grid-cols-3">
            <div class="rounded-md border border-line p-4">
              <p class="text-xs text-muted">Pedidos pagados</p>
              <p class="num mt-1 text-2xl font-extrabold">{{ v.pedidos }}</p>
            </div>
            <div class="rounded-md border border-line p-4">
              <p class="text-xs text-muted">Ingresos</p>
              <p class="num mt-1 text-2xl font-extrabold">{{ v.ingresos_cop | cop }}</p>
            </div>
            <div class="rounded-md border border-line p-4">
              <p class="text-xs text-muted">Ticket promedio</p>
              <p class="num mt-1 text-2xl font-extrabold">{{ v.ticket_promedio_cop | cop }}</p>
            </div>
          </div>

          @if (v.pedidos === 0) {
            <p class="mt-4 rounded-md border border-dashed border-line p-4 text-sm text-muted">
              Todavía no hay ventas pagadas.
            </p>
          } @else {
            <div class="mt-5 grid gap-6 lg:grid-cols-2">
              <div>
                <h3 class="text-sm font-bold">Por categoría y semana</h3>
                <table class="mt-2 w-full text-left text-sm">
                  <thead class="text-xs text-muted">
                    <tr class="border-b border-line">
                      <th class="py-2 pr-3 font-medium">Semana del</th>
                      <th class="py-2 pr-3 font-medium">Categoría</th>
                      <th class="py-2 pr-3 text-right font-medium">Unidades</th>
                      <th class="py-2 text-right font-medium">Ingresos</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (venta of v.por_categoria_y_semana; track venta.semana + venta.categoria) {
                      <tr class="border-b border-line last:border-0">
                        <td class="py-2 pr-3">{{ venta.semana | date: 'dd/MM/yyyy' }}</td>
                        <td class="py-2 pr-3">{{ categoria(venta.categoria) }}</td>
                        <td class="num py-2 pr-3 text-right">{{ venta.unidades }}</td>
                        <td class="num py-2 text-right">{{ venta.ingresos_cop | cop }}</td>
                      </tr>
                    }
                  </tbody>
                </table>
              </div>
              <div>
                <h3 class="text-sm font-bold">Los más vendidos</h3>
                <ol class="mt-2 grid gap-2">
                  @for (accesorio of v.mas_vendidos; track accesorio.nombre; let i = $index) {
                    <li
                      class="flex items-center justify-between gap-3 rounded-md border border-line px-3 py-2 text-sm"
                    >
                      <span
                        ><span class="num mr-2 text-muted">{{ i + 1 }}.</span
                        >{{ accesorio.nombre }}</span
                      >
                      <span class="num text-muted"
                        >{{ accesorio.unidades }} und · {{ accesorio.ingresos_cop | cop }}</span
                      >
                    </li>
                  }
                </ol>
              </div>
            </div>
          }
        } @else {
          <div class="mt-4 h-32 animate-pulse rounded-md bg-surface2" aria-busy="true"></div>
        }
      </section>
    </div>
  `,
})
export class AdminReportes {
  private readonly api = inject(AdminApiService);
  private readonly ui = inject(UiService);

  protected readonly radar = signal<RadarDemandaApi | null>(null);
  protected readonly ventas = signal<ReporteVentasApi | null>(null);
  protected readonly sinAtender = demandaSinAtender;
  protected readonly categoria = textoCategoria;

  constructor() {
    this.cargar();
  }

  cargar(): void {
    this.api.radarDemanda().subscribe({
      next: (radar) => this.radar.set(radar),
      error: (error) =>
        this.ui.avisar(detalleDelError(error, 'No se pudo cargar el radar de demanda'), 'error'),
    });
    this.api.reporteVentas().subscribe({
      next: (ventas) => this.ventas.set(ventas),
      error: (error) =>
        this.ui.avisar(detalleDelError(error, 'No se pudo cargar el reporte de ventas'), 'error'),
    });
  }
}
