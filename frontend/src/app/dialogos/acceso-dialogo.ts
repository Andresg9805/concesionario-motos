import { Component, ElementRef, effect, inject, signal, viewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../core/auth.service';
import { INICIO_POR_ROL, NOMBRE_ROL } from '../core/sesion.service';
import { UiService } from '../core/ui.service';
import { Icono } from '../shared/icono';

type Pestana = 'ingresar' | 'registro';

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
              (click)="cambiar('ingresar')"
            >
              Iniciar sesión
            </button>
            <button
              type="button"
              role="tab"
              class="tab h-10 rounded-md text-sm font-bold"
              [class.text-muted]="pestana() !== 'registro'"
              [attr.aria-selected]="pestana() === 'registro'"
              (click)="cambiar('registro')"
            >
              Crear cuenta
            </button>
          </div>
        </div>

        @if (pestana() === 'ingresar') {
          <form class="flex flex-col gap-4 p-5" novalidate (ngSubmit)="ingresar()">
            @if (aviso()) {
              <p class="rounded-md bg-accentsoft px-3 py-2 text-sm text-accenttext" role="status">
                {{ aviso() }}
              </p>
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
            @if (errorServidor()) {
              <p class="flex items-start gap-2 text-sm text-danger" role="alert">
                <app-icono nombre="alert-circle" class="mt-0.5 h-4 w-4" />{{ errorServidor() }}
              </p>
            }
            <button
              type="submit"
              class="cta inline-flex h-11 items-center justify-center gap-2 rounded-md text-sm font-bold"
              [disabled]="enviando()"
            >
              <app-icono nombre="log-in" class="h-4 w-4" />{{
                enviando() ? 'Ingresando…' : 'Iniciar sesión'
              }}
            </button>
          </form>
        } @else {
          <form class="flex flex-col gap-4 p-5" novalidate (ngSubmit)="registrar()">
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
            @if (errorServidor()) {
              <p class="flex items-start gap-2 text-sm text-danger" role="alert">
                <app-icono nombre="alert-circle" class="mt-0.5 h-4 w-4" />{{ errorServidor() }}
              </p>
            }
            <button
              type="submit"
              class="cta inline-flex h-11 items-center justify-center gap-2 rounded-md text-sm font-bold"
              [disabled]="enviando()"
            >
              <app-icono nombre="user-plus" class="h-4 w-4" />{{
                enviando() ? 'Creando cuenta…' : 'Crear cuenta'
              }}
            </button>
          </form>
        }
      </div>
    </dialog>
  `,
})
export class AccesoDialogo {
  protected readonly ui = inject(UiService);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly dialogo = viewChild.required<ElementRef<HTMLDialogElement>>('dialogo');

  protected readonly pestana = signal<Pestana>('ingresar');
  protected readonly verClave = signal(false);
  protected readonly errores = signal<Record<string, string>>({});
  protected readonly errorServidor = signal('');
  protected readonly aviso = signal('');
  protected readonly enviando = signal(false);

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
        this.limpiarMensajes();
        dialogo.showModal?.();
      } else if (!abierto && dialogo.open) {
        dialogo.close();
      }
    });
  }

  protected cambiar(pestana: Pestana): void {
    this.pestana.set(pestana);
    this.limpiarMensajes();
  }

  protected ingresar(): void {
    const errores: Record<string, string> = {};
    if (!CORREO.test(this.correo.trim())) {
      errores['correo'] = 'Escribe un correo válido.';
    }
    if (!this.clave) {
      errores['clave'] = 'Escribe tu contraseña.';
    }
    this.errores.set(errores);
    this.errorServidor.set('');
    if (Object.keys(errores).length > 0) {
      return;
    }
    this.enviando.set(true);
    this.auth.ingresar(this.correo.trim(), this.clave).subscribe({
      next: (usuario) => {
        this.enviando.set(false);
        this.clave = '';
        this.ui.accesoAbierto.set(false);
        const primerNombre = usuario.nombre.split(' ')[0];
        this.ui.avisar(
          `Hola${primerNombre ? ', ' + primerNombre : ''}. Ingresaste como ${NOMBRE_ROL[usuario.rol].toLowerCase()}.`,
          'ok',
        );
        this.router.navigateByUrl(INICIO_POR_ROL[usuario.rol]);
      },
      error: (error: Error) => {
        this.enviando.set(false);
        this.errorServidor.set(error.message);
      },
    });
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
    this.errorServidor.set('');
    if (Object.keys(errores).length > 0) {
      return;
    }
    this.enviando.set(true);
    this.auth
      .registrar({
        nombre: this.nombre.trim(),
        correo: this.correo.trim(),
        celular: this.celular.trim(),
        contrasena: this.clave,
      })
      .subscribe({
        next: () => {
          this.enviando.set(false);
          this.clave = '';
          this.pestana.set('ingresar');
          this.errores.set({});
          this.aviso.set('Tu cuenta quedó creada. Ahora inicia sesión.');
        },
        error: (error: Error) => {
          this.enviando.set(false);
          this.errorServidor.set(error.message);
        },
      });
  }

  private limpiarMensajes(): void {
    this.errores.set({});
    this.errorServidor.set('');
    this.aviso.set('');
  }
}
