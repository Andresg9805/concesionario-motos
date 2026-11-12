import { Injectable, computed, signal } from '@angular/core';
import { ClaveMarca } from './modelos';

export type Rol = 'CLIENTE' | 'ASESOR' | 'ADMIN';

export interface Usuario {
  id: string;
  nombre: string;
  rol: Rol;
  marca: ClaveMarca | null;
  expira: number;
}

export const NOMBRE_ROL: Record<Rol, string> = {
  CLIENTE: 'Cliente',
  ASESOR: 'Asesor',
  ADMIN: 'Administrador',
};

export const INICIO_POR_ROL: Record<Rol, string> = {
  CLIENTE: '/',
  ASESOR: '/asesor',
  ADMIN: '/admin',
};

const LLAVE_TOKEN = 'candela_token';
const ROLES: readonly Rol[] = ['CLIENTE', 'ASESOR', 'ADMIN'];

function leerToken(): string | null {
  try {
    return localStorage.getItem(LLAVE_TOKEN);
  } catch {
    return null;
  }
}

export function leerUsuario(token: string | null, ahora = Date.now()): Usuario | null {
  if (!token) {
    return null;
  }
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const relleno = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
    const bytes = Uint8Array.from(atob(relleno), (c) => c.charCodeAt(0));
    const datos = JSON.parse(new TextDecoder().decode(bytes));
    const rol = String(datos.rol ?? '').toUpperCase() as Rol;
    const expira = Number(datos.exp) * 1000;
    if (!ROLES.includes(rol) || !Number.isFinite(expira) || expira <= ahora) {
      return null;
    }
    return {
      id: String(datos.sub ?? ''),
      nombre: String(datos.nombre ?? ''),
      rol,
      marca: datos.marca ?? null,
      expira,
    };
  } catch {
    return null;
  }
}

@Injectable({ providedIn: 'root' })
export class SesionService {
  private readonly tokenActual = signal<string | null>(leerToken());

  readonly usuario = computed(() => leerUsuario(this.tokenActual()));
  readonly token = computed(() => (this.usuario() ? this.tokenActual() : null));
  readonly autenticado = computed(() => this.usuario() !== null);
  readonly rol = computed(() => this.usuario()?.rol ?? null);

  guardarToken(token: string): Usuario | null {
    const usuario = leerUsuario(token);
    if (!usuario) {
      return null;
    }
    this.tokenActual.set(token);
    try {
      localStorage.setItem(LLAVE_TOKEN, token);
    } catch {
      return usuario;
    }
    return usuario;
  }

  cerrarSesion(): void {
    this.tokenActual.set(null);
    try {
      localStorage.removeItem(LLAVE_TOKEN);
    } catch {
      return;
    }
  }
}
