import { Component, computed, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { CarritoService } from '../core/carrito.service';
import { INICIO_POR_ROL, NOMBRE_ROL, SesionService } from '../core/sesion.service';
import { TemaService } from '../core/tema.service';
import { UiService } from '../core/ui.service';
import { Icono } from '../shared/icono';

@Component({
  selector: 'app-encabezado',
  imports: [RouterLink, Icono],
  host: { class: 'sticky top-0 z-50 block border-b border-line bg-surface/95 backdrop-blur' },
  template: `
    <div class="gutter mx-auto flex h-[68px] max-w-7xl items-center gap-4">
      <a
        routerLink="/"
        fragment="inicio"
        class="flex min-w-0 items-center gap-3"
        aria-label="Candela Motors, ir al inicio"
      >
        <svg viewBox="0 0 48 48" class="h-11 w-11 shrink-0 text-fg" aria-hidden="true">
          <defs>
            <filter id="brush" x="-10%" y="-10%" width="120%" height="120%">
              <feTurbulence
                type="fractalNoise"
                baseFrequency="0.85"
                numOctaves="2"
                seed="7"
                result="n"
              />
              <feDisplacementMap in="SourceGraphic" in2="n" scale="2.4" />
            </filter>
          </defs>
          <path
            d="M36.5 11.5 A17 17 0 1 0 41.5 28"
            fill="none"
            stroke="currentColor"
            stroke-width="5.2"
            stroke-linecap="round"
            filter="url(#brush)"
          />
          <path
            d="M41.5 28 L42.6 31"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            filter="url(#brush)"
          />
          <text
            x="24"
            y="30.5"
            text-anchor="middle"
            font-family="Shippori Mincho B1, serif"
            font-weight="800"
            font-size="17"
            fill="currentColor"
          >
            燭
          </text>
        </svg>
        <span class="hidden min-w-0 overflow-hidden leading-none min-[440px]:block">
          <span class="block font-display text-[21px] font-extrabold tracking-tight"
            >Candela<span
              class="ml-1.5 hidden align-middle font-sans text-[10px] font-bold tracking-[0.32em] text-muted sm:inline"
              >MOTORS</span
            ></span
          >
          <span class="mt-1 block truncate text-[11px] text-muted"
            >Calidad japonesa <span class="font-display">· 日本品質</span></span
          >
        </span>
      </a>

      <nav class="ml-auto hidden items-center gap-1 lg:flex" aria-label="Principal">
        @for (enlace of enlaces; track enlace.fragmento) {
          <a
            routerLink="/"
            [fragment]="enlace.fragmento"
            class="rounded-md px-3 py-2 text-sm font-medium text-muted hover:bg-surface2 hover:text-fg"
            >{{ enlace.texto }}</a
          >
        }
      </nav>

      <div class="ml-auto flex items-center gap-2 lg:ml-4">
        <button
          type="button"
          class="grid h-10 w-10 place-items-center rounded-md border border-line hover:bg-surface2"
          [attr.aria-label]="
            tema.actual() === 'oscuro' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'
          "
          [attr.title]="tema.actual() === 'oscuro' ? 'Modo claro' : 'Modo oscuro'"
          (click)="tema.alternar()"
        >
          <app-icono
            [nombre]="tema.actual() === 'oscuro' ? 'sun' : 'moon'"
            class="h-[18px] w-[18px]"
          />
        </button>
        @if (sesion.rol() !== 'ASESOR' && sesion.rol() !== 'ADMIN') {
          <a
            routerLink="/carrito"
            class="relative grid h-10 w-10 place-items-center rounded-md border border-line hover:bg-surface2"
            [attr.aria-label]="'Carrito, ' + carrito.unidades() + ' productos'"
            title="Carrito"
          >
            <app-icono nombre="shopping-bag" class="h-[18px] w-[18px]" />
            @if (carrito.unidades() > 0) {
              <span
                class="num absolute -top-1.5 -right-1.5 grid h-5 min-w-5 place-items-center rounded-full bg-accent px-1 text-[11px] font-bold text-onaccent"
                >{{ carrito.unidades() }}</span
              >
            }
          </a>
        }
        @if (sesion.usuario(); as usuario) {
          @if (usuario.rol !== 'CLIENTE') {
            <a
              [routerLink]="inicioPorRol[usuario.rol]"
              class="hidden h-10 items-center rounded-md border border-line px-3 text-sm font-medium hover:bg-surface2 sm:inline-flex"
              >{{ usuario.rol === 'ASESOR' ? 'Mi panel' : 'Administración' }}</a
            >
          }
          <span class="flex items-center gap-2 rounded-md border border-line py-1 pr-1 pl-1">
            <span
              class="grid h-8 w-8 place-items-center rounded bg-accentsoft font-mono text-xs font-semibold text-accenttext"
              >{{ iniciales(usuario.nombre) }}</span
            >
            <span class="hidden min-w-0 leading-tight md:block">
              <span class="block max-w-[140px] truncate text-sm font-medium">{{
                usuario.nombre
              }}</span>
              <span class="block text-[11px] text-muted">{{ nombreRol[usuario.rol] }}</span>
            </span>
            <button
              type="button"
              class="grid h-8 w-8 place-items-center rounded text-muted hover:bg-surface2 hover:text-fg"
              aria-label="Cerrar sesión"
              (click)="salir()"
            >
              <app-icono nombre="log-out" class="h-4 w-4" />
            </button>
          </span>
        } @else {
          <button
            type="button"
            class="cta inline-flex h-10 items-center gap-2 rounded-md px-3 text-sm font-bold sm:px-4"
            (click)="ui.accesoAbierto.set(true)"
          >
            <app-icono nombre="user" class="h-4 w-4" /><span class="hidden sm:inline"
              >Iniciar sesión / Registro</span
            ><span class="sm:hidden">Ingresar</span>
          </button>
        }
        <button
          type="button"
          class="grid h-10 w-10 place-items-center rounded-md border border-line lg:hidden"
          aria-controls="menuMovil"
          [attr.aria-expanded]="menuAbierto()"
          [attr.aria-label]="menuAbierto() ? 'Cerrar menú' : 'Abrir menú'"
          (click)="menuAbierto.set(!menuAbierto())"
        >
          <app-icono [nombre]="iconoMenu()" class="h-5 w-5" />
        </button>
      </div>
    </div>
    @if (menuAbierto()) {
      <nav
        id="menuMovil"
        class="gutter border-t border-line bg-surface pt-2 pb-3 lg:hidden"
        aria-label="Principal móvil"
      >
        <div class="mx-auto grid max-w-7xl grid-cols-2 gap-1 sm:grid-cols-5">
          @for (enlace of enlaces; track enlace.fragmento) {
            <a
              routerLink="/"
              [fragment]="enlace.fragmento"
              class="rounded-md px-3 py-2.5 text-sm font-medium hover:bg-surface2"
              (click)="menuAbierto.set(false)"
              >{{ enlace.texto }}</a
            >
          }
        </div>
      </nav>
    }
    <div class="linea-marca absolute inset-x-0 -bottom-px" aria-hidden="true"></div>
  `,
})
export class Encabezado {
  protected readonly ui = inject(UiService);
  protected readonly sesion = inject(SesionService);
  protected readonly carrito = inject(CarritoService);
  protected readonly tema = inject(TemaService);
  private readonly router = inject(Router);
  protected readonly menuAbierto = signal(false);
  protected readonly nombreRol = NOMBRE_ROL;
  protected readonly inicioPorRol = INICIO_POR_ROL;
  protected readonly iconoMenu = computed(() => (this.menuAbierto() ? 'x' : 'menu'));

  protected readonly enlaces = [
    { fragmento: 'inicio', texto: 'Inicio' },
    { fragmento: 'marcas', texto: 'Marcas' },
    { fragmento: 'catalogo', texto: 'Catálogo' },
    { fragmento: 'accesorios', texto: 'Accesorios' },
    { fragmento: 'cotizar', texto: 'Cotizar' },
  ];

  protected iniciales(nombre: string): string {
    const partes = nombre.trim().split(/\s+/).filter(Boolean);
    return (
      partes
        .slice(0, 2)
        .map((p) => p[0])
        .join('') || 'CM'
    ).toUpperCase();
  }

  protected salir(): void {
    this.sesion.cerrarSesion();
    this.ui.avisar('Cerraste sesión.');
    this.router.navigateByUrl('/');
  }
}
