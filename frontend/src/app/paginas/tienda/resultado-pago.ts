import { Component, computed, inject, input, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, map, of, startWith, switchMap } from 'rxjs';
import { CarritoService } from '../../core/carrito.service';
import { ResultadoPago, TiendaApiService } from '../../core/tienda-api';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';

type Estado =
  { estado: 'cargando' } | { estado: 'error' } | { estado: 'listo'; dato: ResultadoPago };

@Component({
  selector: 'app-resultado-pago',
  imports: [RouterLink, CopPipe, Icono],
  template: `
    <div class="gutter mx-auto max-w-xl py-14">
      @switch (consulta().estado) {
        @case ('cargando') {
          <div class="flex flex-col items-center gap-3 text-center" aria-busy="true">
            <div class="h-14 w-14 animate-pulse rounded-full bg-surface2"></div>
            <p class="text-sm text-muted">Estamos confirmando tu pago con Wompi…</p>
          </div>
        }
        @case ('error') {
          <div class="rounded-lg border border-line bg-surface p-6 text-center" role="alert">
            <h1 class="font-display text-2xl font-extrabold">No pudimos confirmar el pago</h1>
            <p class="mt-2 text-sm text-muted">
              Si Wompi te mostró el pago como aprobado, no lo repitas. Revisa el estado en un
              momento.
            </p>
            <button
              type="button"
              class="cta mt-5 inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-bold"
              (click)="reintentar()"
            >
              <app-icono nombre="refresh-cw" class="h-4 w-4" /> Volver a consultar
            </button>
          </div>
        }
        @case ('listo') {
          @if (resultado(); as r) {
            <div class="rounded-lg border border-line bg-surface p-6 text-center">
              @switch (r.estado_pago) {
                @case ('APROBADO') {
                  <span
                    class="mx-auto grid h-14 w-14 place-items-center rounded-full bg-ok/15 text-ok"
                    ><app-icono nombre="check-circle-2" class="h-7 w-7"
                  /></span>
                  <h1 class="mt-4 font-display text-2xl font-extrabold">¡Pago aprobado!</h1>
                  <p class="mt-2 text-sm text-muted">
                    Tu pedido #{{ r.pedido_id }} por
                    <span class="num font-bold text-fg">{{ r.total_cop | cop }}</span> ya está en
                    preparación.
                  </p>
                  @if (r.numero_guia) {
                    <p class="mt-3 text-sm">
                      Número de guía:
                      <span class="num font-mono font-bold">{{ r.numero_guia }}</span>
                    </p>
                  }
                }
                @case ('PENDIENTE') {
                  <span
                    class="mx-auto grid h-14 w-14 place-items-center rounded-full bg-surface2 text-muted"
                    ><app-icono nombre="info" class="h-7 w-7"
                  /></span>
                  <h1 class="mt-4 font-display text-2xl font-extrabold">Pago en proceso</h1>
                  <p class="mt-2 text-sm text-muted">
                    Wompi todavía está confirmando el pago (pasa con PSE y Nequi). Consulta otra vez
                    en unos segundos.
                  </p>
                  <button
                    type="button"
                    class="cta mt-5 inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-bold"
                    (click)="reintentar()"
                  >
                    <app-icono nombre="refresh-cw" class="h-4 w-4" /> Consultar de nuevo
                  </button>
                }
                @default {
                  <span
                    class="mx-auto grid h-14 w-14 place-items-center rounded-full bg-danger/15 text-danger"
                    ><app-icono nombre="alert-circle" class="h-7 w-7"
                  /></span>
                  <h1 class="mt-4 font-display text-2xl font-extrabold">El pago no se aprobó</h1>
                  @if (r.estado_pedido === 'EXPIRADO') {
                    <p class="mt-2 text-sm text-muted">
                      Pasaron los 15 minutos de reserva y el stock se liberó. Puedes volver a armar
                      el pedido desde el carrito.
                    </p>
                  } @else {
                    <p class="mt-2 text-sm text-muted">
                      No se cobró nada. Tu stock sigue separado hasta las
                      {{ hora(r.reservado_hasta) }}; puedes intentar con otro medio de pago.
                    </p>
                  }
                  <a
                    routerLink="/checkout"
                    class="cta mt-5 inline-flex h-10 items-center rounded-md px-4 text-sm font-bold"
                    >Intentar otra vez</a
                  >
                }
              }
              <a
                routerLink="/"
                class="mt-4 block text-sm font-medium text-muted hover:text-fg hover:underline"
                >Volver al inicio</a
              >
            </div>
          }
        }
      }
    </div>
  `,
})
export class ResultadoPagoPagina {
  readonly pedido = input<string>('');
  readonly id = input<string | null>(null);

  private readonly tienda = inject(TiendaApiService);
  private readonly carrito = inject(CarritoService);
  private readonly intento = signal(0);

  protected readonly consulta = toSignal(
    toObservable(
      computed(() => ({ pedido: this.pedido(), id: this.id(), intento: this.intento() })),
    ).pipe(
      switchMap(({ pedido, id }) =>
        !pedido
          ? of<Estado>({ estado: 'error' })
          : this.tienda.verificarPago(pedido, id).pipe(
              map((dato): Estado => {
                if (dato.estado_pago === 'APROBADO') {
                  this.carrito.vaciar();
                }
                return { estado: 'listo', dato };
              }),
              catchError(() => of<Estado>({ estado: 'error' })),
              startWith<Estado>({ estado: 'cargando' }),
            ),
      ),
    ),
    { initialValue: { estado: 'cargando' } as Estado },
  );

  protected readonly resultado = computed(() => {
    const c = this.consulta();
    return c.estado === 'listo' ? c.dato : null;
  });

  protected reintentar(): void {
    this.intento.update((n) => n + 1);
  }

  protected hora(fecha: string | null): string {
    if (!fecha) {
      return '15 minutos después de crear el pedido';
    }
    return new Date(fecha).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
  }
}
