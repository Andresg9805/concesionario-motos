import { Component, computed, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { Router, RouterLink } from '@angular/router';
import { of, switchMap } from 'rxjs';
import { CarritoService } from '../../core/carrito.service';
import { DatosDireccion, Departamento, TiendaApiService } from '../../core/tienda-api';
import { SesionService } from '../../core/sesion.service';
import { UiService } from '../../core/ui.service';
import { WompiService } from '../../core/wompi';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';

type Campo = 'nombre' | 'telefono' | 'departamento' | 'municipio' | 'direccion';

@Component({
  selector: 'app-checkout',
  imports: [RouterLink, CopPipe, Icono],
  template: `
    <div class="gutter mx-auto max-w-5xl py-10">
      <a
        routerLink="/carrito"
        class="inline-flex items-center gap-1 text-sm font-medium text-muted hover:text-fg"
        ><app-icono nombre="arrow-left" class="h-4 w-4" /> Volver al carrito</a
      >
      <h1 class="mt-4 font-display text-3xl font-extrabold">Datos de envío y pago</h1>

      @if (carrito.vacio()) {
        <p class="mt-6 rounded-lg border border-dashed border-line p-8 text-sm text-muted">
          No hay productos en el carrito.
          <a routerLink="/" fragment="accesorios" class="font-bold text-fg underline"
            >Ir a la tienda</a
          >
        </p>
      } @else {
        <div class="mt-6 grid gap-6 lg:grid-cols-[1fr_340px]">
          <form
            class="flex flex-col gap-4 rounded-lg border border-line bg-surface p-5"
            novalidate
            (submit)="pagar($event)"
          >
            <h2 class="font-display text-lg font-extrabold">¿A dónde lo enviamos?</h2>

            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <label for="nombre" class="text-sm font-medium">Quién recibe</label>
                <input
                  id="nombre"
                  autocomplete="name"
                  class="field mt-1 h-11 w-full rounded-md px-3"
                  [value]="nombre()"
                  [attr.aria-invalid]="!!errores()['nombre']"
                  (input)="nombre.set(texto($event))"
                />
                @if (errores()['nombre']; as error) {
                  <p class="mt-1 text-xs text-danger">{{ error }}</p>
                }
              </div>
              <div>
                <label for="telefono" class="text-sm font-medium">Celular</label>
                <input
                  id="telefono"
                  type="tel"
                  inputmode="numeric"
                  autocomplete="tel"
                  class="field mt-1 h-11 w-full rounded-md px-3"
                  [value]="telefono()"
                  [attr.aria-invalid]="!!errores()['telefono']"
                  (input)="telefono.set(texto($event))"
                />
                @if (errores()['telefono']; as error) {
                  <p class="mt-1 text-xs text-danger">{{ error }}</p>
                }
              </div>
              <div>
                <label for="departamento" class="text-sm font-medium">Departamento</label>
                <select
                  id="departamento"
                  class="field mt-1 h-11 w-full rounded-md px-3"
                  [attr.aria-invalid]="!!errores()['departamento']"
                  (change)="elegirDepartamento(texto($event))"
                >
                  <option value="" [selected]="!departamento()">Elige uno</option>
                  @for (d of departamentos(); track d.codigo) {
                    <option [value]="d.codigo" [selected]="d.codigo === departamento()">
                      {{ d.nombre }}
                    </option>
                  }
                </select>
                @if (errores()['departamento']; as error) {
                  <p class="mt-1 text-xs text-danger">{{ error }}</p>
                }
              </div>
              <div>
                <label for="municipio" class="text-sm font-medium">Municipio</label>
                @if (municipios(); as lista) {
                  <select
                    id="municipio"
                    class="field mt-1 h-11 w-full rounded-md px-3"
                    [attr.aria-invalid]="!!errores()['municipio']"
                    (change)="elegirMunicipio(texto($event))"
                  >
                    <option value="" [selected]="!municipio()">Elige uno</option>
                    @for (m of lista; track m.codigo) {
                      <option [value]="m.codigo" [selected]="m.codigo === municipioCodigo()">
                        {{ m.nombre }}
                      </option>
                    }
                  </select>
                } @else {
                  <input
                    id="municipio"
                    class="field mt-1 h-11 w-full rounded-md px-3"
                    [disabled]="!departamento()"
                    [value]="municipio()"
                    [attr.aria-invalid]="!!errores()['municipio']"
                    (input)="municipio.set(texto($event)); municipioCodigo.set(null)"
                  />
                }
                @if (errores()['municipio']; as error) {
                  <p class="mt-1 text-xs text-danger">{{ error }}</p>
                }
              </div>
            </div>
            <div>
              <label for="direccion" class="text-sm font-medium">Dirección</label>
              <input
                id="direccion"
                autocomplete="street-address"
                placeholder="Calle 26 # 13-19"
                class="field mt-1 h-11 w-full rounded-md px-3"
                [value]="direccion()"
                [attr.aria-invalid]="!!errores()['direccion']"
                (input)="direccion.set(texto($event))"
              />
              @if (errores()['direccion']; as error) {
                <p class="mt-1 text-xs text-danger">{{ error }}</p>
              }
            </div>
            <div>
              <label for="detalle" class="text-sm font-medium"
                >Apartamento, barrio o indicaciones
                <span class="text-muted">(opcional)</span></label
              >
              <input
                id="detalle"
                class="field mt-1 h-11 w-full rounded-md px-3"
                [value]="detalle()"
                (input)="detalle.set(texto($event))"
              />
            </div>

            @if (errorServidor()) {
              <p class="rounded-md border border-danger/40 bg-danger/10 p-3 text-sm" role="alert">
                {{ errorServidor() }}
              </p>
            }

            <button
              type="submit"
              class="cta inline-flex h-12 items-center justify-center gap-2 rounded-md text-sm font-bold disabled:opacity-60"
              [disabled]="enviando()"
            >
              <app-icono nombre="wallet" class="h-4 w-4" />
              {{ enviando() ? 'Preparando el pago…' : 'Pagar con Wompi' }}
            </button>
            <p class="text-xs text-muted">
              Pagas con tarjeta, Nequi o PSE en la ventana de Wompi (ambiente de pruebas). Al crear
              el pedido separamos tu stock por 15 minutos.
            </p>
          </form>

          <aside
            class="flex flex-col gap-3 self-start rounded-lg border border-line bg-surface p-5 lg:sticky lg:top-24"
          >
            <h2 class="font-display text-lg font-extrabold">Tu pedido</h2>
            <ul class="flex flex-col gap-2 text-sm">
              @for (linea of carrito.lineas(); track linea.accesorio.id) {
                <li class="flex justify-between gap-3">
                  <span class="text-muted"
                    >{{ linea.cantidad }} × {{ linea.accesorio.nombre }}</span
                  >
                  <span class="num shrink-0">{{ linea.subtotal | cop }}</span>
                </li>
              }
            </ul>
            <div class="flex flex-col gap-1.5 border-t border-line pt-3 text-sm">
              <div class="flex justify-between">
                <span class="text-muted">Subtotal</span>
                <span class="num">{{ carrito.subtotal() | cop }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted">Envío</span>
                <span class="num">
                  @if (envio(); as d) {
                    {{ d.costo_envio_cop | cop }}
                  } @else {
                    Elige el departamento
                  }
                </span>
              </div>
              @if (envio(); as d) {
                <p class="text-xs text-muted">
                  Llega en {{ d.dias_envio }}
                  {{ d.dias_envio === 1 ? 'día hábil' : 'días hábiles' }}
                </p>
              }
              <div class="mt-1 flex justify-between border-t border-line pt-2 font-bold">
                <span>Total</span>
                <span class="num">{{ total() | cop }}</span>
              </div>
            </div>
            <p class="text-xs text-muted">
              El total final lo confirma el servidor al crear el pedido.
            </p>
          </aside>
        </div>
      }
    </div>
  `,
})
export class Checkout {
  protected readonly carrito = inject(CarritoService);
  private readonly tienda = inject(TiendaApiService);
  private readonly wompi = inject(WompiService);
  private readonly sesion = inject(SesionService);
  private readonly ui = inject(UiService);
  private readonly router = inject(Router);

  protected readonly nombre = signal(this.sesion.usuario()?.nombre ?? '');
  protected readonly telefono = signal('');
  protected readonly departamento = signal('');
  protected readonly municipio = signal('');
  protected readonly municipioCodigo = signal<string | null>(null);
  protected readonly direccion = signal('');
  protected readonly detalle = signal('');

  protected readonly errores = signal<Partial<Record<Campo, string>>>({});
  protected readonly errorServidor = signal('');
  protected readonly enviando = signal(false);

  private readonly cargaDepartamentos = toSignal(this.tienda.departamentos(), {
    initialValue: { lista: [] as Departamento[], respaldo: true },
  });
  protected readonly departamentos = computed(() => this.cargaDepartamentos().lista);

  protected readonly municipios = toSignal(
    toObservable(this.departamento).pipe(
      switchMap((codigo) => (codigo ? this.tienda.municipios(codigo) : of(null))),
    ),
    { initialValue: null },
  );

  protected readonly envio = computed(
    () => this.departamentos().find((d) => d.codigo === this.departamento()) ?? null,
  );
  protected readonly total = computed(
    () => this.carrito.subtotal() + (this.envio()?.costo_envio_cop ?? 0),
  );

  protected texto(evento: Event): string {
    return (evento.target as HTMLInputElement | HTMLSelectElement).value;
  }

  protected elegirDepartamento(codigo: string): void {
    this.departamento.set(codigo);
    this.municipio.set('');
    this.municipioCodigo.set(null);
  }

  protected elegirMunicipio(codigo: string): void {
    const encontrado = this.municipios()?.find((m) => m.codigo === codigo);
    this.municipioCodigo.set(encontrado?.codigo ?? null);
    this.municipio.set(encontrado?.nombre ?? '');
  }

  protected pagar(evento: Event): void {
    evento.preventDefault();
    const errores = this.validar();
    this.errores.set(errores);
    this.errorServidor.set('');
    if (Object.keys(errores).length > 0 || this.enviando()) {
      return;
    }
    const datos: DatosDireccion = {
      nombre_recibe: this.nombre().trim(),
      telefono: this.telefono().replace(/\D/g, ''),
      departamento_codigo: this.departamento(),
      municipio_codigo: this.municipioCodigo(),
      municipio_nombre: this.municipio().trim(),
      direccion: this.direccion().trim(),
      detalle: this.detalle().trim(),
    };
    const items = this.carrito
      .lineas()
      .map((l) => ({ accesorio_id: l.accesorio.id, cantidad: l.cantidad }));
    this.enviando.set(true);
    this.tienda.crearPedido(datos, items).subscribe({
      next: (pedido) => {
        const retorno = `${location.origin}/pago/resultado?pedido=${pedido.pedido_id}`;
        this.wompi
          .abrir(pedido.wompi, retorno)
          .then((transaccion) => {
            this.enviando.set(false);
            this.router.navigate(['/pago/resultado'], {
              queryParams: { pedido: pedido.pedido_id, id: transaccion?.id ?? null },
            });
          })
          .catch(() => {
            this.enviando.set(false);
            this.errorServidor.set(
              'No se pudo abrir la ventana de Wompi. Revisa tu conexión e inténtalo otra vez.',
            );
          });
      },
      error: (error: { status?: number }) => {
        this.enviando.set(false);
        this.errorServidor.set(this.mensaje(error.status ?? 0));
      },
    });
  }

  private mensaje(estado: number): string {
    if (estado === 0 || estado === 404) {
      return 'El pago todavía no está disponible: el servidor de la tienda no respondió.';
    }
    if (estado === 401 || estado === 403) {
      this.ui.destinoTrasAcceso.set('/checkout');
      this.ui.accesoAbierto.set(true);
      return 'Tu sesión venció. Ingresa otra vez para terminar la compra.';
    }
    if (estado === 409) {
      return 'Uno de los productos ya no tiene stock suficiente. Revisa el carrito.';
    }
    return 'No pudimos crear el pedido. Inténtalo de nuevo en un momento.';
  }

  private validar(): Partial<Record<Campo, string>> {
    const errores: Partial<Record<Campo, string>> = {};
    if (this.nombre().trim().length < 3) {
      errores.nombre = 'Escribe el nombre de quien recibe.';
    }
    if (!/^3\d{9}$/.test(this.telefono().replace(/\D/g, ''))) {
      errores.telefono = 'Escribe un celular de 10 dígitos que empiece por 3.';
    }
    if (!this.departamento()) {
      errores.departamento = 'Elige el departamento.';
    }
    if (this.municipio().trim().length < 2) {
      errores.municipio = 'Elige o escribe el municipio.';
    }
    if (this.direccion().trim().length < 5) {
      errores.direccion = 'Escribe la dirección completa.';
    }
    return errores;
  }
}
