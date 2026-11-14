import { Component, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { CarritoService } from '../../core/carrito.service';
import { SesionService } from '../../core/sesion.service';
import { UiService } from '../../core/ui.service';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';
import { IlustracionAccesorio } from '../../shared/ilustracion-accesorio';

@Component({
  selector: 'app-carrito',
  imports: [RouterLink, CopPipe, Icono, IlustracionAccesorio],
  template: `
    <div class="gutter mx-auto max-w-5xl py-10">
      <a
        routerLink="/"
        fragment="accesorios"
        class="inline-flex items-center gap-1 text-sm font-medium text-muted hover:text-fg"
        ><app-icono nombre="arrow-left" class="h-4 w-4" /> Seguir comprando</a
      >
      <h1 class="mt-4 font-display text-3xl font-extrabold">Tu carrito</h1>

      @if (carrito.vacio()) {
        <div
          class="mt-6 flex flex-col items-start gap-3 rounded-lg border border-dashed border-line p-8"
        >
          <p class="font-display text-lg font-extrabold">Tu carrito está vacío.</p>
          <p class="text-sm text-muted">Agrega cascos, chaquetas y más desde la tienda.</p>
          <a
            routerLink="/"
            fragment="accesorios"
            class="cta inline-flex h-10 items-center rounded-md px-4 text-sm font-bold"
            >Ir a la tienda</a
          >
        </div>
      } @else {
        <div class="mt-6 grid gap-6 lg:grid-cols-[1fr_320px]">
          <ul class="flex flex-col gap-3">
            @for (linea of carrito.lineas(); track linea.accesorio.id) {
              <li
                class="grid grid-cols-[72px_1fr] gap-4 rounded-lg border border-line bg-surface p-3 sm:grid-cols-[96px_1fr_auto]"
              >
                <div class="grid aspect-square place-items-center rounded-md bg-surface2 p-2">
                  <app-ilustracion-accesorio [tipo]="linea.accesorio.ilustracion" />
                </div>
                <div class="min-w-0">
                  <p class="text-xs text-muted">{{ linea.accesorio.categoria }}</p>
                  <p class="font-bold">{{ linea.accesorio.nombre }}</p>
                  <p class="num mt-1 text-sm text-muted">{{ linea.accesorio.precio | cop }} c/u</p>
                </div>
                <div
                  class="col-span-2 flex items-center justify-between gap-4 sm:col-span-1 sm:flex-col sm:items-end"
                >
                  <div
                    class="inline-flex items-center rounded-md border border-line"
                    role="group"
                    [attr.aria-label]="'Cantidad de ' + linea.accesorio.nombre"
                  >
                    <button
                      type="button"
                      class="grid h-9 w-9 place-items-center hover:bg-surface2"
                      aria-label="Quitar una unidad"
                      (click)="carrito.fijar(linea.accesorio, linea.cantidad - 1)"
                    >
                      −
                    </button>
                    <span class="num w-8 text-center text-sm font-bold">{{ linea.cantidad }}</span>
                    <button
                      type="button"
                      class="grid h-9 w-9 place-items-center hover:bg-surface2 disabled:opacity-40"
                      aria-label="Agregar una unidad"
                      [disabled]="linea.cantidad >= linea.accesorio.stock"
                      (click)="carrito.fijar(linea.accesorio, linea.cantidad + 1)"
                    >
                      +
                    </button>
                  </div>
                  <div class="text-right">
                    <p class="num font-bold">{{ linea.subtotal | cop }}</p>
                    <button
                      type="button"
                      class="text-xs text-muted hover:text-fg hover:underline"
                      (click)="carrito.quitar(linea.accesorio.id)"
                    >
                      Quitar
                    </button>
                  </div>
                </div>
              </li>
            }
          </ul>

          <aside
            class="flex flex-col gap-3 self-start rounded-lg border border-line bg-surface p-5 lg:sticky lg:top-24"
          >
            <h2 class="font-display text-lg font-extrabold">Resumen</h2>
            <div class="flex justify-between text-sm">
              <span class="text-muted">{{ carrito.unidades() }} productos</span>
              <span class="num font-bold">{{ carrito.subtotal() | cop }}</span>
            </div>
            <p class="text-xs text-muted">
              El envío se calcula con el departamento de destino en el siguiente paso.
            </p>
            <button
              type="button"
              class="cta inline-flex h-11 items-center justify-center gap-2 rounded-md text-sm font-bold"
              (click)="continuar()"
            >
              Continuar con la compra <app-icono nombre="arrow-right" class="h-4 w-4" />
            </button>
            @if (!esCliente()) {
              <p class="text-xs text-muted">Para pagar necesitas iniciar sesión como cliente.</p>
            }
          </aside>
        </div>
      }
    </div>
  `,
})
export class Carrito {
  protected readonly carrito = inject(CarritoService);
  private readonly sesion = inject(SesionService);
  private readonly ui = inject(UiService);
  private readonly router = inject(Router);

  protected esCliente(): boolean {
    return this.sesion.rol() === 'CLIENTE';
  }

  protected continuar(): void {
    if (this.esCliente()) {
      this.router.navigate(['/checkout']);
      return;
    }
    if (this.sesion.autenticado()) {
      this.ui.avisar('Solo las cuentas de cliente pueden comprar accesorios.', 'error');
      return;
    }
    this.ui.destinoTrasAcceso.set('/checkout');
    this.ui.accesoAbierto.set(true);
  }
}
