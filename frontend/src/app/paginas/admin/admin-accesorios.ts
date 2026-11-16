import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  AccesorioAdminApi,
  AccesorioEntradaApi,
  AdminApiService,
  detalleDelError,
} from '../../core/admin-api';
import { UiService } from '../../core/ui.service';
import { CopPipe } from '../../shared/cop.pipe';
import { Icono } from '../../shared/icono';

const CATEGORIAS: readonly { clave: string; nombre: string }[] = [
  { clave: 'CASCO', nombre: 'Cascos' },
  { clave: 'CHAQUETA', nombre: 'Chaquetas' },
  { clave: 'GUANTES', nombre: 'Guantes' },
  { clave: 'RODILLERA', nombre: 'Rodilleras' },
  { clave: 'HOMBRERA', nombre: 'Hombreras' },
  { clave: 'MALETA', nombre: 'Maletas' },
  { clave: 'MANTENIMIENTO', nombre: 'Mantenimiento' },
];

function accesorioVacio(): AccesorioEntradaApi {
  return {
    sku: '',
    nombre: '',
    categoria: 'CASCO',
    fabricante: '',
    descripcion: '',
    precio_cop: 0,
    stock: 0,
    imagen_url: '',
  };
}

@Component({
  selector: 'app-admin-accesorios',
  imports: [CopPipe, FormsModule, Icono],
  template: `
    @if (formulario(); as f) {
      <form class="rounded-lg border border-line bg-surface p-5" novalidate (ngSubmit)="guardar()">
        <div class="flex items-center justify-between gap-3">
          <h2 class="font-display text-xl font-extrabold">
            {{ editando() ? 'Editar accesorio' : 'Nuevo accesorio' }}
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
            SKU
            <input class="field h-10 rounded-md px-3" name="sku" [(ngModel)]="f.sku" />
          </label>
          <label class="grid gap-1 text-sm font-medium sm:col-span-1 lg:col-span-2">
            Nombre
            <input class="field h-10 rounded-md px-3" name="nombre" [(ngModel)]="f.nombre" />
          </label>
          <label class="grid gap-1 text-sm font-medium">
            Fabricante
            <input
              class="field h-10 rounded-md px-3"
              name="fabricante"
              list="fabricantes"
              [(ngModel)]="f.fabricante"
            />
            <datalist id="fabricantes">
              @for (nombre of fabricantes(); track nombre) {
                <option [value]="nombre"></option>
              }
            </datalist>
          </label>
          <label class="grid gap-1 text-sm font-medium">
            Categoría
            <select class="field h-10 rounded-md px-3" name="categoria" [(ngModel)]="f.categoria">
              @for (c of categorias; track c.clave) {
                <option [value]="c.clave">{{ c.nombre }}</option>
              }
            </select>
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
          <app-icono nombre="check" class="h-4 w-4" /> Guardar accesorio
        </button>
      </form>
    }

    <div class="mt-6 flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap gap-2" aria-label="Filtrar por categoría">
        <button
          type="button"
          class="chip inline-flex h-9 items-center rounded-full border border-line px-4 text-sm"
          [attr.aria-pressed]="categoria() === null"
          (click)="categoria.set(null)"
        >
          Todas
        </button>
        @for (c of categorias; track c.clave) {
          <button
            type="button"
            class="chip inline-flex h-9 items-center rounded-full border border-line px-4 text-sm"
            [attr.aria-pressed]="categoria() === c.clave"
            (click)="categoria.set(c.clave)"
          >
            {{ c.nombre }}
          </button>
        }
      </div>
      <button
        type="button"
        class="cta inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-bold"
        (click)="nuevo()"
      >
        <app-icono nombre="plus" class="h-4 w-4" /> Nuevo accesorio
      </button>
    </div>

    @if (cargando()) {
      <div class="mt-4 h-40 animate-pulse rounded-lg bg-surface2" aria-busy="true"></div>
    } @else {
      <div class="mt-4 overflow-x-auto rounded-lg border border-line">
        <table class="w-full min-w-[720px] text-sm">
          <thead class="bg-surface2 text-left text-xs text-muted">
            <tr>
              <th class="px-4 py-3 font-medium">Accesorio</th>
              <th class="px-4 py-3 font-medium">Categoría</th>
              <th class="px-4 py-3 text-right font-medium">Precio</th>
              <th class="px-4 py-3 text-right font-medium">Stock</th>
              <th class="px-4 py-3"><span class="sr-only">Acciones</span></th>
            </tr>
          </thead>
          <tbody>
            @for (a of filtrados(); track a.id) {
              <tr class="border-t border-line">
                <td class="px-4 py-3">
                  <span class="block text-[11px] font-bold tracking-wider text-muted uppercase">{{
                    a.fabricante
                  }}</span>
                  <span class="font-bold">{{ a.nombre }}</span>
                  <span class="block font-mono text-xs text-muted">{{ a.sku }}</span>
                </td>
                <td class="px-4 py-3">{{ nombreCategoria(a.categoria) }}</td>
                <td class="num px-4 py-3 text-right">{{ a.precio_cop | cop }}</td>
                <td class="num px-4 py-3 text-right" [class.text-danger]="a.stock === 0">
                  {{ a.stock }}
                </td>
                <td class="px-4 py-3">
                  <div class="flex justify-end gap-2">
                    @if (porEliminar() === a.id) {
                      <span class="self-center text-xs text-muted">¿Eliminar?</span>
                      <button
                        type="button"
                        class="h-8 rounded-md border border-line px-3 text-xs font-bold text-danger"
                        (click)="eliminar(a)"
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
                        (click)="editar(a)"
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        class="h-8 rounded-md border border-line px-3 text-xs text-danger"
                        [attr.aria-label]="'Eliminar ' + a.nombre"
                        (click)="porEliminar.set(a.id)"
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
      <p class="mt-2 text-xs text-muted">
        {{ filtrados().length }} de {{ accesorios().length }} accesorios
      </p>
    }
  `,
})
export class AdminAccesorios {
  private readonly api = inject(AdminApiService);
  private readonly ui = inject(UiService);

  protected readonly categorias = CATEGORIAS;

  protected readonly cargando = signal(true);
  protected readonly accesorios = signal<AccesorioAdminApi[]>([]);
  protected readonly categoria = signal<string | null>(null);
  protected readonly formulario = signal<AccesorioEntradaApi | null>(null);
  protected readonly editando = signal<number | null>(null);
  protected readonly guardando = signal(false);
  protected readonly porEliminar = signal<number | null>(null);

  protected readonly filtrados = computed(() => {
    const categoria = this.categoria();
    return categoria
      ? this.accesorios().filter((a) => a.categoria === categoria)
      : this.accesorios();
  });

  protected readonly fabricantes = computed(() =>
    [
      ...new Set(
        this.accesorios()
          .map((a) => a.fabricante)
          .filter(Boolean),
      ),
    ].sort(),
  );

  constructor() {
    this.api.accesorios().subscribe({
      next: (accesorios) => {
        this.accesorios.set(accesorios);
        this.cargando.set(false);
      },
      error: (error) => {
        this.cargando.set(false);
        this.ui.avisar(detalleDelError(error, 'No se pudieron cargar los accesorios'), 'error');
      },
    });
  }

  protected nombreCategoria(clave: string): string {
    return CATEGORIAS.find((c) => c.clave === clave)?.nombre ?? clave;
  }

  nuevo(): void {
    this.editando.set(null);
    this.formulario.set(accesorioVacio());
  }

  editar(accesorio: AccesorioAdminApi): void {
    const { id, ...datos } = accesorio;
    this.editando.set(id);
    this.formulario.set({ ...datos });
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
    const peticion = id ? this.api.actualizarAccesorio(id, datos) : this.api.crearAccesorio(datos);
    peticion.subscribe({
      next: (guardado) => {
        this.accesorios.update((lista) =>
          id ? lista.map((a) => (a.id === id ? guardado : a)) : [...lista, guardado],
        );
        this.guardando.set(false);
        this.cerrar();
        this.ui.avisar(`${guardado.nombre} guardado`, 'ok');
      },
      error: (error) => {
        this.guardando.set(false);
        this.ui.avisar(detalleDelError(error, 'No se pudo guardar el accesorio'), 'error');
      },
    });
  }

  eliminar(accesorio: AccesorioAdminApi): void {
    this.api.eliminarAccesorio(accesorio.id).subscribe({
      next: () => {
        this.accesorios.update((lista) => lista.filter((a) => a.id !== accesorio.id));
        this.porEliminar.set(null);
        this.ui.avisar(`${accesorio.nombre} eliminado`, 'ok');
      },
      error: (error) => {
        this.porEliminar.set(null);
        this.ui.avisar(detalleDelError(error, 'No se pudo eliminar el accesorio'), 'error');
      },
    });
  }
}
