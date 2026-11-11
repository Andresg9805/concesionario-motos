import { Injectable, computed, signal } from '@angular/core';

const LLAVE_TOKEN = 'candela_token';

function leerToken(): string | null {
  try {
    return localStorage.getItem(LLAVE_TOKEN);
  } catch {
    return null;
  }
}

@Injectable({ providedIn: 'root' })
export class SesionService {
  private readonly tokenActual = signal<string | null>(leerToken());

  readonly token = this.tokenActual.asReadonly();
  readonly autenticado = computed(() => this.tokenActual() !== null);

  guardarToken(token: string): void {
    this.tokenActual.set(token);
    try {
      localStorage.setItem(LLAVE_TOKEN, token);
    } catch {
      return;
    }
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
