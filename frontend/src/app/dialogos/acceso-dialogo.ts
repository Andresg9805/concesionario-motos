import { Component, ElementRef, effect, inject, signal, viewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LISTA_MARCAS } from '../core/marcas';
import { UiService } from '../core/ui.service';
import { Icono } from '../shared/icono';

type Pestana = 'ingresar' | 'registro';
type Rol = 'CLIENTE' | 'ASESOR' | 'ADMIN';

const CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

@Component({
  selector: 'app-acceso-dialogo',
  imports: [FormsModule, Icono],
  template: `
    <dialog
      #dialogo
      aria-labelledby="tituloAcceso"
      class="theme-t m-auto"
      (close)="ui.accesoAbierto.set(false)"
    >
      <div
        class="sheet w-[min(460px,calc(100vw-32px))] overflow-hidden rounded-xl border border-line bg-surface shadow-2xl"
      >
        <div class="flex items-start justify-between gap-4 border-b border-line p-5">
          <h2 id="tituloAcceso" class="font-display text-xl font-extrabold">
            Accede a Candela Motors
          </h2>
          <button
            type="button"
            class="grid h-9 w-9 shrink-0 place-items-center rounded-md hover:bg-surface2"
            aria-label="Cerrar"
            (click)="ui.accesoAbierto.set(false)"
          >
            <app-icono nombre="x" class="h-5 w-5" />
          </button>
        </div>
        <div class="px-5 pt-4">
          <div
            role="tablist"
            aria-label="Tipo de acceso"
            class="grid grid-cols-2 gap-1 rounded-lg bg-surface2 p-1"
          >
            <button
              type="button"
              role="tab"
              class="tab h-10 rounded-md text-sm font-bold"
              [class.text-muted]="pestana() !== 'ingresar'"
              [attr.aria-selected]="pestana() === 'ingresar'"
              (click)="pestana.set('ingresar')"
            >
              Iniciar sesión
            </button>
            <button
              type="button"
              role="tab"
              class="tab h-10 rounded-md text-sm font-bold"
              [class.text-muted]="pestana() !== 'registro'"
              [attr.aria-selected]="pestana() === 'registro'"
              (click)="pestana.set('registro')"
            >
              Crear cuenta
            </button>
          </div>
        </div>

        @if (pestana() === 'ingresar') {
          <form class="flex flex-col gap-4 p-5" novalidate (ngSubmit)="ingresar()">
            <fieldset>
              <legend class="text-sm font-medium">Ingresar como</legend>
              <div role="radiogroup" aria-label="Rol" class="mt-1.5 grid grid-cols-3 gap-2">
                @for (opcion of roles; track opcion.rol) {
                  <button
                    type="button"
                    role="radio"
                    class="chip flex h-14 flex-col items-center justify-center gap-0.5 rounded-md border border-line text-xs font-bold"
                    [attr.aria-checked]="rol() === opcion.rol"
                    (click)="rol.set(opcion.rol)"
                  >
                    <app-icono [nombre]="opcion.icono" class="h-4 w-4" />{{ opcion.texto }}
                  </button>
                }
              </div>
            </fieldset>
            @if (rol() === 'ASESOR') {
              <label class="text-sm font-medium" for="marcaAsesor"
                >Marca de especialidad
                <select
                  id="marcaAsesor"
                  name="marcaAsesor"
                  class="field mt-1 h-11 w-full rounded-md px-3"
                  [(ngModel)]="marcaAsesor"
                >
                  @for (marca of marcas; track marca.clave) {
                    <option [value]="marca.clave">{{ marca.nombre }}</option>
                  }
                </select>
              </label>
            }
            <label class="text-sm font-medium" for="correoIngreso"
              >Correo electrónico
              <input
                id="correoIngreso"
                name="correo"
                type="email"
                autocomplete="email"
                class="field mt-1 h-11 w-full rounded-md px-3"
                placeholder="nombre@correo.com"
                [attr.aria-invalid]="!!errores()['correo']"
                [(ngModel)]="correo"
              />
              @if (errores()['correo']) {
                <span class="mt-1 block text-xs text-danger">{{ errores()['correo'] }}</span>
              }
            </label>
            <label class="text-sm font-medium" for="claveIngreso"
              >Contraseña
              <span class="relative mt-1 block">
                <input
                  id="claveIngreso"
                  name="clave"
                  [type]="verClave() ? 'text' : 'password'"
                  autocomplete="current-password"
                  class="field h-11 w-full rounded-md pr-11 pl-3"
                  [attr.aria-invalid]="!!errores()['clave']"
                  [(ngModel)]="clave"
                />
                <button
                  type="button"
                  class="absolute top-1 right-1 grid h-9 w-9 place-items-center rounded text-muted hover:text-fg"
                  [attr.aria-label]="verClave() ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                  (click)="verClave.set(!verClave())"
                >
                  <app-icono [nombre]="verClave() ? 'eye-off' : 'eye'" class="h-4 w-4" />
                </button>
              </span>
              @if (errores()['clave']) {
                <span class="mt-1 block text-xs text-danger">{{ errores()['clave'] }}</span>
              }
            </label>
            <button
              type="submit"
              class="cta inline-flex h-11 items-center justify-center gap-2 rounded-md text-sm font-bold"
            >
              <app-icono nombre="log-in" class="h-4 w-4" />Iniciar sesión
            </button>
            <p class="text-xs text-muted">
              El inicio de sesión se conecta con la API cuando esté listo el login con JWT (#27).
            </p>
          </form>
        } @else {
          <form class="flex flex-col gap-4 p-5" novalidate (ngSubmit)="registrar()">
            <p class="rounded-md bg-surface2 px-3 py-2 text-xs text-muted">
              Las cuentas nuevas son de cliente. Las cuentas de asesor y administrador las crea el
              administrador.
            </p>
            <label class="text-sm font-medium" for="nombreRegistro"
              >Nombre completo
              <input
                id="nombreRegistro"
                name="nombre"
                autocomplete="name"
                class="field mt-1 h-11 w-full rounded-md px-3"
                [attr.aria-invalid]="!!errores()['nombre']"
                [(ngModel)]="nombre"
              />
              @if (errores()['nombre']) {
                <span class="mt-1 block text-xs text-danger">{{ errores()['nombre'] }}</span>
              }
            </label>
            <div class="grid gap-4 sm:grid-cols-2">
              <label class="text-sm font-medium" for="correoRegistro"
                >Correo
                <input
                  id="correoRegistro"
                  name="correo"
                  type="email"
                  autocomplete="email"
                  class="field mt-1 h-11 w-full rounded-md px-3"
                  [attr.aria-invalid]="!!errores()['correo']"
                  [(ngModel)]="correo"
                />
                @if (errores()['correo']) {
                  <span class="mt-1 block text-xs text-danger">{{ errores()['correo'] }}</span>
                }
              </label>
              <label class="text-sm font-medium" for="celularRegistro"
                >Celular
                <input
                  id="celularRegistro"
                  name="celular"
                  type="tel"
                  inputmode="numeric"
                  autocomplete="tel"
                  maxlength="10"
                  class="field num mt-1 h-11 w-full rounded-md px-3"
                  placeholder="3001234567"
                  [attr.aria-invalid]="!!errores()['celular']"
                  [(ngModel)]="celular"
                />
                @if (errores()['celular']) {
                  <span class="mt-1 block text-xs text-danger">{{ errores()['celular'] }}</span>
                }
              </label>
            </div>
            <label class="text-sm font-medium" for="claveRegistro"
              >Contraseña
              <input
                id="claveRegistro"
                name="clave"
                type="password"
                autocomplete="new-password"
                class="field mt-1 h-11 w-full rounded-md px-3"
                [attr.aria-invalid]="!!errores()['clave']"
                [(ngModel)]="clave"
              />
              <span class="mt-1 block text-xs text-muted"
                >Mínimo 8 caracteres, con al menos un número.</span
              >
              @if (errores()['clave']) {
                <span class="mt-1 block text-xs text-danger">{{ errores()['clave'] }}</span>
              }
            </label>
            <label class="flex items-start gap-2 text-xs text-muted" for="terminosRegistro">
              <input
                id="terminosRegistro"
                name="terminos"
                type="checkbox"
                class="mt-0.5 h-4 w-4"
                [(ngModel)]="terminos"
              />
              <span
                >Autorizo el tratamiento de mis datos personales según la Ley 1581 de 2012.</span
              >
            </label>
            @if (errores()['terminos']) {
              <span class="-mt-3 text-xs text-danger">{{ errores()['terminos'] }}</span>
            }
            <button
              type="submit"
              class="cta inline-flex h-11 items-center justify-center gap-2 rounded-md text-sm font-bold"
            >
              <app-icono nombre="user-plus" class="h-4 w-4" />Crear cuenta
            </button>
          </form>
        }
      </div>
    </dialog>
  `,
})
export class AccesoDialogo {
  protected readonly ui = inject(UiService);
  private readonly dialogo = viewChild.required<ElementRef<HTMLDialogElement>>('dialogo');

  protected readonly marcas = LISTA_MARCAS;
  protected readonly roles: { rol: Rol; texto: string; icono: string }[] = [
    { rol: 'CLIENTE', texto: 'Cliente', icono: 'user' },
    { rol: 'ASESOR', texto: 'Asesor', icono: 'headset' },
    { rol: 'ADMIN', texto: 'Administrador', icono: 'shield' },
  ];

  protected readonly pestana = signal<Pestana>('ingresar');
  protected readonly rol = signal<Rol>('CLIENTE');
  protected readonly verClave = signal(false);
  protected readonly errores = signal<Record<string, string>>({});

  protected marcaAsesor = 'honda';
  protected nombre = '';
  protected correo = '';
  protected celular = '';
  protected clave = '';
  protected terminos = false;

  constructor() {
    effect(() => {
      const abierto = this.ui.accesoAbierto();
      const dialogo = this.dialogo().nativeElement;
      if (abierto && !dialogo.open) {
        this.errores.set({});
        dialogo.showModal?.();
      } else if (!abierto && dialogo.open) {
        dialogo.close();
      }
    });
  }

  protected ingresar(): void {
    const errores: Record<string, string> = {};
    if (!CORREO.test(this.correo.trim())) {
      errores['correo'] = 'Escribe un correo válido.';
    }
    if (this.clave.length < 8) {
      errores['clave'] = 'La contraseña tiene mínimo 8 caracteres.';
    }
    this.errores.set(errores);
    if (Object.keys(errores).length === 0) {
      this.ui.avisar('Datos válidos. El ingreso real se conecta con el login de la API (#27).');
    }
  }

  protected registrar(): void {
    const errores: Record<string, string> = {};
    if (this.nombre.trim().length < 3) {
      errores['nombre'] = 'Escribe tu nombre completo.';
    }
    if (!CORREO.test(this.correo.trim())) {
      errores['correo'] = 'Escribe un correo válido.';
    }
    if (!/^3\d{9}$/.test(this.celular.trim())) {
      errores['celular'] = 'El celular tiene 10 dígitos y empieza por 3.';
    }
    if (this.clave.length < 8 || !/\d/.test(this.clave)) {
      errores['clave'] = 'Mínimo 8 caracteres, con al menos un número.';
    }
    if (!this.terminos) {
      errores['terminos'] = 'Necesitamos tu autorización para crear la cuenta.';
    }
    this.errores.set(errores);
    if (Object.keys(errores).length === 0) {
      this.ui.avisar('Datos válidos. El registro real se conecta con la API (#27).');
    }
  }
}
