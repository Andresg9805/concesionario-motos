import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';
import {
  AdminApiService,
  MotoAdminApi,
  MotoEntradaApi,
  detalleDelError,
  licenciaPorCilindraje,
} from '../../core/admin-api';
import { NOMBRE_TIPO, ORDEN_TIPOS } from '../../core/marcas';
import { MarcaResumenApi } from '../../core/motos-api';
import { UiService } from '../../core/ui.service';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';

function motoVacia(marcaId: number): MotoEntradaApi {
  return {
    marca_id: marcaId,
    modelo: '',
    anio: new Date().getFullYear(),
    cilindraje_cc: 150,
    tipo: 'NAKED',
    precio_cop: 0,
    stock: 0,
    consumo_km_galon: 100,
    costo_mantenimiento_km_cop: 50,
    descripcion: '',
    imagen_url: '',
  };
}

@Component({
  selector: 'app-admin-motos',
  imports: [CopPipe, FormsModule, Icono],
  template: `
    @if (formulario(); as f) {
      <form class="rounded-lg border border-line bg-surface p-5" novalidate (ngSubmit)="guardar()">
        <div class="flex items-center justify-between gap-3">
          <h2 class="font-display text-xl font-extrabold">
            {{ editando() ? 'Editar moto' : 'Nueva moto' }}
          </h2>
          <button
            type="button"
            class="inline-flex h-9 items-center gap-2 rounded-md border border-line px-3 text-sm"
            (click)="cerrar()"
          >
            <app-icono nombre="x" class="h-4 w-4" /> Cancelar
          </button>
        </div>
        <div class="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <label class="grid gap-1 text-sm font-medium">
            Marca
            <select class="field h-10 rounded-md px-3" name="marca" [(ngModel)]="f.marca_id">
              @for (m of marcas(); track m.id) {
                <option [ngValue]="m.id">{{ m.nombre }}</option>
              }
            </select>
          </label>
          <label class="grid gap-1 text-sm font-medium">
            Modelo
            <input
              class="field h-10 rounded-md px-3"
              name="modelo"
              required
              [(ngModel)]="f.modelo"
            />
          </label>
          <label class="grid gap-1 text-sm font-medium">
            Tipo
            <select class="field h-10 rounded-md px-3" name="tipo" [(ngModel)]="f.tipo">
              @for (t of tipos; track t) {
                <option [value]="t">{{ nombreTipo[t] }}</option>
              }
            </select>
          </label>
          <label class="grid gap-1 text-sm font-medium">
            Año
            <input
              class="field h-10 rounded-md px-3"
              type="number"
              name="anio"
              [(ngModel)]="f.anio"
            />
          </label>
          <label class="grid gap-1 text-sm font-medium">
            <span
              >Cilindraje (cc)
              <span class="font-normal text-muted"
                >· licencia {{ licencia(f.cilindraje_cc) }}</span
              ></span
            >
            <input
              class="field h-10 rounded-md px-3"
              type="number"
              name="cilindraje"
              [(ngModel)]="f.cilindraje_cc"
            />
          </label>
          <label class="grid gap-1 text-sm font-medium">
            Precio (COP)
            <input
              class="field h-10 rounded-md px-3"
              type="number"
              name="precio"
              [(ngModel)]="f.precio_cop"
            />
          </label>
          <label class="grid gap-1 text-sm font-medium">
            Stock
            <input
              class="field h-10 rounded-md px-3"
              type="number"
              name="stock"
              [(ngModel)]="f.stock"
            />
          </label>
          <label class="grid gap-1 text-sm font-medium">
            Consumo (km por galón)
            <input
              class="field h-10 rounded-md px-3"
              type="number"
              name="consumo"
              [(ngModel)]="f.consumo_km_galon"
            />
          </label>
          <label class="grid gap-1 text-sm font-medium">
            Mantenimiento por km (COP)
            <input
              class="field h-10 rounded-md px-3"
              type="number"
              name="mantenimiento"
              [(ngModel)]="f.costo_mantenimiento_km_cop"
            />
          </label>
          <label class="grid gap-1 text-sm font-medium sm:col-span-2 lg:col-span-3">
            Imagen (URL)
            <input class="field h-10 rounded-md px-3" name="imagen" [(ngModel)]="f.imagen_url" />
          </label>
          <label class="grid gap-1 text-sm font-medium sm:col-span-2 lg:col-span-4">
            Descripción
            <textarea
              class="field min-h-20 rounded-md p-3"
              name="descripcion"
              maxlength="1000"
              [(ngModel)]="f.descripcion"
            ></textarea>
          </label>
        </div>
        <button
          type="submit"
          class="cta mt-4 inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-bold"
          [disabled]="guardando()"
        >
          <app-icono nombre="check" class="h-4 w-4" /> Guardar moto
        </button>
      </form>
    }

    <div class="mt-6 flex flex-wrap items-center justify-between gap-3">
      <label class="relative block w-full max-w-xs">
        <span class="sr-only">Buscar moto</span>
        <app-icono
          nombre="search"
          class="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-muted"
        />
        <input
          class="field h-10 w-full rounded-md pr-3 pl-9"
          placeholder="Buscar por modelo o marca"
          [ngModel]="busqueda()"
          (ngModelChange)="busqueda.set($event)"
        />
      </label>
      <button
        type="button"
        class="cta inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-bold"
        (click)="nueva()"
      >
        <app-icono nombre="plus" class="h-4 w-4" /> Nueva moto
      </button>
    </div>

    @if (cargando()) {
      <div class="mt-4 h-40 animate-pulse rounded-lg bg-surface2" aria-busy="true"></div>
    } @else {
      <div class="mt-4 overflow-x-auto rounded-lg border border-line">
        <table class="w-full min-w-[720px] text-sm">
          <thead class="bg-surface2 text-left text-xs text-muted">
            <tr>
              <th class="px-4 py-3 font-medium">Moto</th>
              <th class="px-4 py-3 font-medium">Tipo</th>
              <th class="px-4 py-3 font-medium">Cilindraje</th>
              <th class="px-4 py-3 text-right font-medium">Precio</th>
              <th class="px-4 py-3 text-right font-medium">Stock</th>
              <th class="px-4 py-3"><span class="sr-only">Acciones</span></th>
            </tr>
          </thead>
          <tbody>
            @for (m of filtradas(); track m.id) {
              <tr class="border-t border-line">
                <td class="px-4 py-3">
                  <span class="font-bold">{{ m.modelo }}</span>
                  <span class="block text-xs text-muted">{{ m.marca.nombre }} · {{ m.anio }}</span>
                </td>
                <td class="px-4 py-3">{{ tipoTexto(m.tipo) }}</td>
                <td class="num px-4 py-3">{{ m.cilindraje_cc }} cc · {{ m.categoria_licencia }}</td>
                <td class="num px-4 py-3 text-right">{{ m.precio_cop | cop }}</td>
                <td class="num px-4 py-3 text-right" [class.text-danger]="m.stock === 0">
                  {{ m.stock }}
                </td>
                <td class="px-4 py-3">
                  <div class="flex justify-end gap-2">
                    @if (porEliminar() === m.id) {
                      <span class="self-center text-xs text-muted">¿Eliminar?</span>
                      <button
                        type="button"
                        class="h-8 rounded-md border border-line px-3 text-xs font-bold text-danger"
                        (click)="eliminar(m)"
                      >
                        Sí
                      </button>
                      <button
                        type="button"
                        class="h-8 rounded-md border border-line px-3 text-xs"
                        (click)="porEliminar.set(null)"
                      >
                        No
                      </button>
                    } @else {
                      <button
                        type="button"
                        class="h-8 rounded-md border border-line px-3 text-xs font-bold hover:border-accent"
                        (click)="editar(m)"
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        class="h-8 rounded-md border border-line px-3 text-xs text-danger"
                        [attr.aria-label]="'Eliminar ' + m.modelo"
                        (click)="porEliminar.set(m.id)"
                      >
                        <app-icono nombre="x" class="h-3.5 w-3.5" />
                      </button>
                    }
                  </div>
                </td>
              </tr>
            }
          </tbody>
        </table>
      </div>
      <p class="mt-2 text-xs text-muted">{{ filtradas().length }} de {{ motos().length }} motos</p>
    }
  `,
})
export class AdminMotos {
  private readonly api = inject(AdminApiService);
  private readonly ui = inject(UiService);

  protected readonly tipos = ORDEN_TIPOS;
  protected readonly nombreTipo = NOMBRE_TIPO;
  protected readonly licencia = licenciaPorCilindraje;

  protected tipoTexto(tipo: string): string {
    return (NOMBRE_TIPO as Record<string, string>)[tipo] ?? tipo;
  }

  protected readonly cargando = signal(true);
  protected readonly motos = signal<MotoAdminApi[]>([]);
  protected readonly marcas = signal<MarcaResumenApi[]>([]);
  protected readonly busqueda = signal('');
  protected readonly formulario = signal<MotoEntradaApi | null>(null);
  protected readonly editando = signal<number | null>(null);
  protected readonly guardando = signal(false);
  protected readonly porEliminar = signal<number | null>(null);

  protected readonly filtradas = computed(() => {
    const texto = this.busqueda().trim().toLowerCase();
    return this.motos().filter(
      (m) => !texto || `${m.marca.nombre} ${m.modelo}`.toLowerCase().includes(texto),
    );
  });

  constructor() {
    forkJoin({ motos: this.api.motos(), marcas: this.api.marcas() }).subscribe({
      next: ({ motos, marcas }) => {
        this.motos.set(motos);
        this.marcas.set(marcas);
        this.cargando.set(false);
      },
      error: (error) => {
        this.cargando.set(false);
        this.ui.avisar(detalleDelError(error, 'No se pudieron cargar las motos'), 'error');
      },
    });
  }

  nueva(): void {
    this.editando.set(null);
    this.formulario.set(motoVacia(this.marcas()[0]?.id ?? 1));
  }

  editar(moto: MotoAdminApi): void {
    this.editando.set(moto.id);
    this.formulario.set({
      marca_id: moto.marca.id,
      modelo: moto.modelo,
      anio: moto.anio,
      cilindraje_cc: moto.cilindraje_cc,
      tipo: moto.tipo,
      precio_cop: moto.precio_cop,
      stock: moto.stock,
      consumo_km_galon: moto.consumo_km_galon,
      costo_mantenimiento_km_cop: moto.costo_mantenimiento_km_cop,
      descripcion: moto.descripcion,
      imagen_url: moto.imagen_url,
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  cerrar(): void {
    this.formulario.set(null);
    this.editando.set(null);
  }

  guardar(): void {
    const datos = this.formulario();
    if (!datos) {
      return;
    }
    const id = this.editando();
    this.guardando.set(true);
    const peticion = id ? this.api.actualizarMoto(id, datos) : this.api.crearMoto(datos);
    peticion.subscribe({
      next: (guardada) => {
        const conStock = { ...guardada, stock: datos.stock };
        this.motos.update((lista) =>
          id ? lista.map((m) => (m.id === id ? conStock : m)) : [...lista, conStock],
        );
        this.guardando.set(false);
        this.cerrar();
        this.ui.avisar(`${guardada.modelo} guardada`, 'ok');
      },
      error: (error) => {
        this.guardando.set(false);
        this.ui.avisar(detalleDelError(error, 'No se pudo guardar la moto'), 'error');
      },
    });
  }

  eliminar(moto: MotoAdminApi): void {
    this.api.eliminarMoto(moto.id).subscribe({
      next: () => {
        this.motos.update((lista) => lista.filter((m) => m.id !== moto.id));
        this.porEliminar.set(null);
        this.ui.avisar(`${moto.modelo} eliminada`, 'ok');
      },
      error: (error) => {
        this.porEliminar.set(null);
        this.ui.avisar(detalleDelError(error, 'No se pudo eliminar la moto'), 'error');
      },
    });
  }
}
