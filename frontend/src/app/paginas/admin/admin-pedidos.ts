import { Component, computed, inject, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  AdminApiService,
  GrupoPedidos,
  PedidoAdminApi,
  detalleDelError,
  grupoDelPedido,
  siguientePaso,
} from '../../core/admin-api';
import { EstadoEnvio, NOMBRE_ESTADO_PEDIDO, PASOS_ENVIO, pasoActual } from '../../core/cuenta-api';
import { UiService } from '../../core/ui.service';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';

const GRUPOS: readonly { clave: GrupoPedidos; nombre: string }[] = [
  { clave: 'despachar', nombre: 'Por despachar' },
  { clave: 'pendientes', nombre: 'Sin pagar' },
  { clave: 'entregados', nombre: 'Entregados' },
  { clave: 'todos', nombre: 'Todos' },
];

const FORMATO = new Intl.DateTimeFormat('es-CO', {
  day: 'numeric',
  month: 'short',
  hour: 'numeric',
  minute: '2-digit',
});

@Component({
  selector: 'app-admin-pedidos',
  imports: [CopPipe, FormsModule, Icono],
  template: `
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap gap-2" aria-label="Filtrar pedidos">
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
      <button
        type="button"
        class="inline-flex h-9 items-center gap-2 rounded-md border border-line px-3 text-sm text-muted hover:text-fg"
        (click)="cargar()"
      >
        <app-icono nombre="refresh-cw" class="h-4 w-4" /> Actualizar
      </button>
    </div>

    @if (cargando()) {
      <div class="mt-6 h-32 animate-pulse rounded-lg bg-surface2" aria-busy="true"></div>
    } @else if (filtrados().length === 0) {
      <p
        class="mt-6 rounded-lg border border-dashed border-line p-8 text-center text-sm text-muted"
      >
        No hay pedidos en este grupo.
      </p>
    } @else {
      <ul class="mt-6 grid gap-4">
        @for (p of filtrados(); track p.id) {
          <li class="rounded-lg border border-line bg-surface p-5">
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p class="num font-mono text-xs text-muted">
                  Pedido #{{ p.id }} · {{ fecha(p.creado_en) }}
                </p>
                <p class="mt-1 font-bold">{{ p.cliente_nombre }}</p>
                <p class="text-sm text-muted">{{ p.cliente_correo }}</p>
              </div>
              <div class="text-right">
                <p class="num font-display text-xl font-extrabold">{{ p.total_cop | cop }}</p>
                <p class="text-xs text-muted">{{ nombreEstado[p.estado] ?? p.estado }}</p>
              </div>
            </div>

            <p class="mt-3 text-sm text-muted">
              @for (item of p.items; track item.accesorio_id; let ultimo = $last) {
                {{ item.cantidad }} × {{ item.nombre }}{{ ultimo ? '' : ' · ' }}
              }
            </p>

            @if (p.envio; as envio) {
              <div class="mt-4 border-t border-line pt-4">
                <p class="text-sm">
                  Guía <span class="num font-mono font-bold">{{ envio.numero_guia }}</span>
                </p>
                <ol class="mt-3 flex gap-1" aria-label="Avance del envío">
                  @for (paso of pasos; track paso.estado; let i = $index) {
                    <li class="flex-1">
                      <span
                        class="block h-1.5 rounded-full"
                        [class.bg-accent]="i <= pasoActual(envio.estado)"
                        [class.bg-surface2]="i > pasoActual(envio.estado)"
                      ></span>
                      <span
                        class="mt-1 block text-[11px]"
                        [class.font-bold]="i === pasoActual(envio.estado)"
                        [class.text-muted]="i !== pasoActual(envio.estado)"
                        >{{ paso.nombre }}</span
                      >
                    </li>
                  }
                </ol>
                @if (siguiente(envio.estado); as sig) {
                  <div class="mt-4 flex flex-wrap items-end gap-2">
                    <label class="grid flex-1 gap-1 text-sm">
                      <span class="text-xs text-muted">Nota para el cliente (opcional)</span>
                      <input
                        class="field h-9 rounded-md px-3"
                        maxlength="200"
                        [name]="'nota' + envio.id"
                        [(ngModel)]="notas[envio.id]"
                      />
                    </label>
                    <button
                      type="button"
                      class="cta inline-flex h-9 items-center gap-2 rounded-md px-3 text-sm font-bold"
                      [disabled]="ocupado() === envio.id"
                      (click)="avanzar(p, sig.estado)"
                    >
                      <app-icono nombre="arrow-right" class="h-4 w-4" /> Marcar
                      {{ sig.nombre.toLowerCase() }}
                    </button>
                  </div>
                }
              </div>
            }
          </li>
        }
      </ul>
    }
  `,
})
export class AdminPedidos {
  private readonly api = inject(AdminApiService);
  private readonly ui = inject(UiService);

  readonly porDespachar = output<number>();

  protected readonly grupos = GRUPOS;
  protected readonly pasos = PASOS_ENVIO;
  protected readonly pasoActual = pasoActual;
  protected readonly siguiente = siguientePaso;
  protected readonly nombreEstado = NOMBRE_ESTADO_PEDIDO;
  protected readonly notas: Record<number, string> = {};

  protected readonly cargando = signal(true);
  protected readonly pedidos = signal<PedidoAdminApi[]>([]);
  protected readonly grupo = signal<GrupoPedidos>('despachar');
  protected readonly ocupado = signal<number | null>(null);

  protected readonly conteo = computed(() => {
    const conteo: Record<GrupoPedidos, number> = {
      despachar: 0,
      pendientes: 0,
      entregados: 0,
      todos: this.pedidos().length,
    };
    for (const pedido of this.pedidos()) {
      conteo[grupoDelPedido(pedido)]++;
    }
    return conteo;
  });

  protected readonly filtrados = computed(() =>
    this.grupo() === 'todos'
      ? this.pedidos()
      : this.pedidos().filter((p) => grupoDelPedido(p) === this.grupo()),
  );

  constructor() {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.api.pedidos().subscribe({
      next: (pedidos) => {
        this.pedidos.set(pedidos);
        this.cargando.set(false);
        this.porDespachar.emit(this.conteo().despachar);
      },
      error: (error) => {
        this.cargando.set(false);
        this.ui.avisar(detalleDelError(error, 'No se pudieron cargar los pedidos'), 'error');
      },
    });
  }

  avanzar(pedido: PedidoAdminApi, estado: EstadoEnvio): void {
    const envio = pedido.envio;
    if (!envio) {
      return;
    }
    this.ocupado.set(envio.id);
    this.api.avanzarEnvio(envio.id, estado, this.notas[envio.id] ?? '').subscribe({
      next: (actualizado) => {
        this.pedidos.update((lista) =>
          lista.map((p) => (p.id === pedido.id ? { ...p, envio: actualizado } : p)),
        );
        this.notas[envio.id] = '';
        this.ocupado.set(null);
        this.porDespachar.emit(this.conteo().despachar);
        this.ui.avisar(`Pedido #${pedido.id}: envío actualizado`, 'ok');
      },
      error: (error) => {
        this.ocupado.set(null);
        this.ui.avisar(detalleDelError(error, 'No se pudo actualizar el envío'), 'error');
      },
    });
  }

  protected fecha(valor: string): string {
    return FORMATO.format(new Date(valor));
  }
}
