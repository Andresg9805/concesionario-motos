import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { AtencionApi } from '../../core/atencion-api';
import {
  CuentaApiService,
  DireccionApi,
  NOMBRE_ESTADO_COTIZACION,
  PASOS_ENVIO,
  PedidoDetalleApi,
  PedidoResumenApi,
  estadoDelPedido,
  fechaDelPaso,
  pasoActual,
} from '../../core/cuenta-api';
import { SesionService } from '../../core/sesion.service';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';

type Pestana = 'pedidos' | 'cotizaciones' | 'direcciones';
type Carga = 'cargando' | 'error' | 'listo';

const FORMATO_FECHA = new Intl.DateTimeFormat('es-CO', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
});

const FORMATO_FECHA_HORA = new Intl.DateTimeFormat('es-CO', {
  day: 'numeric',
  month: 'short',
  hour: 'numeric',
  minute: '2-digit',
});

@Component({
  selector: 'app-cuenta',
  imports: [CopPipe, Icono, RouterLink],
  template: `
    <section class="relative overflow-hidden border-b border-line bg-surface2">
      <div class="resplandor pointer-events-none absolute inset-0" aria-hidden="true"></div>
      <div class="gutter relative mx-auto max-w-5xl py-10">
        <p class="eyebrow eyebrow-marca text-muted">Mi cuenta</p>
        <h1 class="mt-2 font-display text-3xl font-extrabold md:text-[42px]">
          Hola, {{ primerNombre() }}
        </h1>
        <p class="mt-2 max-w-xl text-sm text-muted">
          Aquí sigues tus compras de la tienda, las cotizaciones que pediste y tus direcciones de
          envío.
        </p>
      </div>
    </section>

    <div class="gutter mx-auto max-w-5xl py-8">
      <div role="tablist" aria-label="Secciones de la cuenta" class="flex flex-wrap gap-2">
        @for (p of pestanas; track p.clave) {
          <button
            type="button"
            role="tab"
            class="tab inline-flex h-10 items-center gap-2 rounded-md border border-line px-4 text-sm font-bold"
            [attr.aria-selected]="pestana() === p.clave"
            (click)="pestana.set(p.clave)"
          >
            <app-icono [nombre]="p.icono" class="h-4 w-4" /> {{ p.nombre }}
            <span class="num opacity-80">{{ conteo()[p.clave] }}</span>
          </button>
        }
      </div>

      @switch (carga()) {
        @case ('cargando') {
          <div class="mt-6 grid gap-3" aria-busy="true">
            @for (i of [1, 2, 3]; track i) {
              <div class="h-24 animate-pulse rounded-lg bg-surface2"></div>
            }
          </div>
        }
        @case ('error') {
          <div class="mt-6 rounded-lg border border-line bg-surface p-6 text-center" role="alert">
            <p class="font-bold">No pudimos cargar tu cuenta</p>
            <p class="mt-1 text-sm text-muted">Revisa tu conexión y vuelve a intentarlo.</p>
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
          @switch (pestana()) {
            @case ('pedidos') {
              @if (pedidos().length === 0) {
                <div class="mt-6 rounded-lg border border-dashed border-line p-8 text-center">
                  <p class="text-sm text-muted">Todavía no has comprado nada en la tienda.</p>
                  <a
                    routerLink="/tienda"
                    class="cta mt-4 inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-bold"
                  >
                    <app-icono nombre="shopping-bag" class="h-4 w-4" /> Ir a la tienda
                  </a>
                </div>
              } @else {
                <ul class="mt-6 grid gap-4">
                  @for (p of pedidos(); track p.pedido_id) {
                    <li class="rounded-lg border border-line bg-surface p-5">
                      <div class="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p class="num font-mono text-xs text-muted">
                            Pedido #{{ p.pedido_id }} · {{ fecha(p.creado_en) }}
                          </p>
                          <p class="mt-1 font-display text-xl font-extrabold">
                            <span class="num">{{ p.total_cop | cop }}</span>
                          </p>
                          <p class="text-xs text-muted">
                            Incluye envío de <span class="num">{{ p.costo_envio_cop | cop }}</span>
                          </p>
                        </div>
                        <span
                          class="rounded-full px-3 py-1 text-xs font-bold"
                          [class]="claseEstadoPedido(p.estado_pedido)"
                          >{{ estadoPedido(p) }}</span
                        >
                      </div>

                      @if (p.estado_pedido === 'PENDIENTE_PAGO' && p.reservado_hasta) {
                        <p class="mt-3 flex items-center gap-2 text-sm text-muted">
                          <app-icono nombre="clock" class="h-4 w-4" />
                          Guardamos tus productos hasta las {{ hora(p.reservado_hasta) }}
                        </p>
                      }
                      @if (p.numero_guia) {
                        <p class="mt-3 text-sm">
                          Guía de envío
                          <span class="num font-mono font-bold">{{ p.numero_guia }}</span>
                        </p>
                      }

                      <button
                        type="button"
                        class="mt-4 inline-flex h-9 items-center gap-2 rounded-md border border-line px-3 text-sm font-bold hover:border-accent"
                        [attr.aria-expanded]="abierto() === p.pedido_id"
                        (click)="alternar(p.pedido_id)"
                      >
                        <app-icono
                          [nombre]="abierto() === p.pedido_id ? 'chevron-left' : 'chevron-right'"
                          class="h-4 w-4"
                        />
                        {{ abierto() === p.pedido_id ? 'Ocultar detalle' : 'Ver detalle y envío' }}
                      </button>

                      @if (abierto() === p.pedido_id) {
                        @if (detalle(); as d) {
                          <div class="mt-4 grid gap-6 border-t border-line pt-4 md:grid-cols-2">
                            <div>
                              <h3 class="text-sm font-bold">Productos</h3>
                              <ul class="mt-2 grid gap-2 text-sm">
                                @for (item of d.items; track item.accesorio_id) {
                                  <li class="flex justify-between gap-3">
                                    <span>{{ item.cantidad }} × {{ item.nombre }}</span>
                                    <span class="num">{{ item.subtotal_cop | cop }}</span>
                                  </li>
                                }
                              </ul>
                            </div>
                            <div>
                              <h3 class="text-sm font-bold">Envío</h3>
                              @if (d.estado_envio) {
                                <ol class="mt-3 grid gap-3" aria-label="Seguimiento del envío">
                                  @for (paso of pasos; track paso.estado; let i = $index) {
                                    <li class="flex items-start gap-3">
                                      <span
                                        class="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-full border text-[11px] font-bold"
                                        [class.bg-accent]="i <= pasoActual(d.estado_envio)"
                                        [class.text-onaccent]="i <= pasoActual(d.estado_envio)"
                                        [class.border-accent]="i <= pasoActual(d.estado_envio)"
                                        [class.border-line]="i > pasoActual(d.estado_envio)"
                                      >
                                        @if (i <= pasoActual(d.estado_envio)) {
                                          <app-icono nombre="check" class="h-3.5 w-3.5" />
                                        } @else {
                                          {{ i + 1 }}
                                        }
                                      </span>
                                      <div class="text-sm">
                                        <p
                                          class="font-bold"
                                          [class.text-muted]="i > pasoActual(d.estado_envio)"
                                        >
                                          {{ paso.nombre }}
                                        </p>
                                        @if (fechaPaso(d, paso.estado); as f) {
                                          <p class="text-xs text-muted">{{ fechaHora(f) }}</p>
                                        }
                                      </div>
                                    </li>
                                  }
                                </ol>
                              } @else {
                                <p class="mt-2 text-sm text-muted">
                                  El envío empieza cuando se confirma el pago.
                                </p>
                              }
                            </div>
                          </div>
                        } @else {
                          <div class="mt-4 h-24 animate-pulse rounded-lg bg-surface2"></div>
                        }
                      }
                    </li>
                  }
                </ul>
              }
            }
            @case ('cotizaciones') {
              @if (cotizaciones().length === 0) {
                <p
                  class="mt-6 rounded-lg border border-dashed border-line p-8 text-center text-sm text-muted"
                >
                  No tienes cotizaciones. Cuando cotices una moto con este correo, aparece aquí.
                </p>
              } @else {
                <ul class="mt-6 grid gap-4 md:grid-cols-2">
                  @for (c of cotizaciones(); track c.codigo) {
                    <li class="flex flex-col rounded-lg border border-line bg-surface p-5">
                      <div class="flex items-start justify-between gap-3">
                        <div>
                          <p class="num font-mono text-xs text-muted">
                            {{ c.codigo }} · {{ fecha(c.creada_en) }}
                          </p>
                          <h3 class="mt-1 font-display text-xl font-extrabold">
                            {{ c.moto.marca.nombre }} {{ c.moto.modelo }}
                          </h3>
                        </div>
                        <span class="shrink-0 rounded-full bg-surface2 px-3 py-1 text-xs font-bold">
                          {{ nombreEstado[c.estado] ?? c.estado }}
                        </span>
                      </div>
                      @if (c.cuota_mensual_cop) {
                        <p class="mt-3 text-sm">
                          Cuota estimada
                          <span class="num font-bold">{{ c.cuota_mensual_cop | cop }}</span> al mes
                        </p>
                      }
                      <div class="mt-auto flex flex-wrap items-center justify-between gap-2 pt-4">
                        <p class="text-sm text-muted">Tu asesor: {{ c.asesor.nombre }}</p>
                        <a
                          class="inline-flex h-9 items-center gap-2 rounded-md border border-line px-3 text-sm font-bold hover:border-accent"
                          target="_blank"
                          rel="noopener"
                          [href]="whatsapp(c)"
                        >
                          <app-icono nombre="send" class="h-4 w-4" /> Escribirle
                        </a>
                      </div>
                    </li>
                  }
                </ul>
              }
            }
            @case ('direcciones') {
              @if (direcciones().length === 0) {
                <p
                  class="mt-6 rounded-lg border border-dashed border-line p-8 text-center text-sm text-muted"
                >
                  Aún no tienes direcciones. Se guardan cuando haces una compra.
                </p>
              } @else {
                <ul class="mt-6 grid gap-4 md:grid-cols-2">
                  @for (d of direcciones(); track d.id) {
                    <li class="rounded-lg border border-line bg-surface p-5 text-sm">
                      <p class="flex items-center gap-2 font-bold">
                        <app-icono nombre="map-pin" class="h-4 w-4 text-muted" />
                        {{ d.direccion }}
                      </p>
                      @if (d.detalle) {
                        <p class="mt-1 text-muted">{{ d.detalle }}</p>
                      }
                      <p class="mt-1 text-muted">{{ d.municipio_nombre }}</p>
                      <p class="mt-3">Recibe {{ d.nombre_recibe }} · {{ d.telefono }}</p>
                    </li>
                  }
                </ul>
              }
            }
          }
        }
      }
    </div>
  `,
})
export class Cuenta {
  private readonly api = inject(CuentaApiService);
  private readonly sesion = inject(SesionService);

  protected readonly pestanas: readonly { clave: Pestana; nombre: string; icono: string }[] = [
    { clave: 'pedidos', nombre: 'Mis pedidos', icono: 'shopping-bag' },
    { clave: 'cotizaciones', nombre: 'Mis cotizaciones', icono: 'file-text' },
    { clave: 'direcciones', nombre: 'Direcciones', icono: 'map-pin' },
  ];
  protected readonly pasos = PASOS_ENVIO;
  protected readonly nombreEstado = NOMBRE_ESTADO_COTIZACION;
  protected readonly estadoPedido = estadoDelPedido;
  protected readonly pasoActual = pasoActual;

  protected readonly pestana = signal<Pestana>('pedidos');
  protected readonly carga = signal<Carga>('cargando');
  protected readonly pedidos = signal<PedidoResumenApi[]>([]);
  protected readonly cotizaciones = signal<AtencionApi[]>([]);
  protected readonly direcciones = signal<DireccionApi[]>([]);
  protected readonly abierto = signal<number | null>(null);
  protected readonly detalle = signal<PedidoDetalleApi | null>(null);

  protected readonly primerNombre = computed(
    () => this.sesion.usuario()?.nombre.split(' ')[0] ?? '',
  );

  protected readonly conteo = computed<Record<Pestana, number>>(() => ({
    pedidos: this.pedidos().length,
    cotizaciones: this.cotizaciones().length,
    direcciones: this.direcciones().length,
  }));

  constructor() {
    this.cargar();
  }

  cargar(): void {
    this.carga.set('cargando');
    forkJoin({
      pedidos: this.api.misPedidos(),
      cotizaciones: this.api.misCotizaciones(),
      direcciones: this.api.misDirecciones(),
    }).subscribe({
      next: ({ pedidos, cotizaciones, direcciones }) => {
        this.pedidos.set(pedidos);
        this.cotizaciones.set(cotizaciones);
        this.direcciones.set(direcciones);
        this.carga.set('listo');
      },
      error: () => this.carga.set('error'),
    });
  }

  alternar(id: number): void {
    if (this.abierto() === id) {
      this.abierto.set(null);
      return;
    }
    this.abierto.set(id);
    this.detalle.set(null);
    this.api.miPedido(id).subscribe({
      next: (detalle) => {
        if (this.abierto() === id) {
          this.detalle.set(detalle);
        }
      },
      error: () => this.abierto.set(null),
    });
  }

  protected fechaPaso(
    detalle: PedidoDetalleApi,
    estado: PedidoDetalleApi['estado_envio'],
  ): string | null {
    return estado ? fechaDelPaso(detalle.eventos, estado) : null;
  }

  protected claseEstadoPedido(estado: string): string {
    if (estado === 'PAGADO') {
      return 'bg-ok/15 text-ok';
    }
    return estado === 'EXPIRADO' ? 'bg-danger/15 text-danger' : 'bg-accent text-onaccent';
  }

  protected whatsapp(cotizacion: AtencionApi): string {
    const numero = cotizacion.asesor.whatsapp.replace(/\D/g, '');
    const conPais = numero.length === 10 ? `57${numero}` : numero;
    const mensaje = `Hola ${cotizacion.asesor.nombre.split(' ')[0]}, te escribo por mi cotización ${cotizacion.codigo} de la ${cotizacion.moto.marca.nombre} ${cotizacion.moto.modelo}.`;
    return `https://wa.me/${conPais}?text=${encodeURIComponent(mensaje)}`;
  }

  protected fecha(valor: string): string {
    return FORMATO_FECHA.format(new Date(valor));
  }

  protected fechaHora(valor: string): string {
    return FORMATO_FECHA_HORA.format(new Date(valor));
  }

  protected hora(valor: string): string {
    return new Intl.DateTimeFormat('es-CO', { hour: 'numeric', minute: '2-digit' }).format(
      new Date(valor),
    );
  }
}
