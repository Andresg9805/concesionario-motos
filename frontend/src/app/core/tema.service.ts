import { DOCUMENT } from '@angular/common';
import { Injectable, effect, inject, signal } from '@angular/core';

export type Tema = 'oscuro' | 'claro';

const LLAVE = 'cm-tema';

function leerGuardado(): Tema {
  try {
    return localStorage.getItem(LLAVE) === 'claro' ? 'claro' : 'oscuro';
  } catch {
    return 'oscuro';
  }
}

@Injectable({ providedIn: 'root' })
export class TemaService {
  private readonly documento = inject(DOCUMENT);
  private readonly tema = signal<Tema>(leerGuardado());

  readonly actual = this.tema.asReadonly();

  constructor() {
    effect(() => {
      const tema = this.tema();
      const raiz = this.documento.documentElement;
      if (tema === 'claro') {
        raiz.setAttribute('data-theme', 'light');
      } else {
        raiz.removeAttribute('data-theme');
      }
      try {
        localStorage.setItem(LLAVE, tema);
      } catch {
        return;
      }
    });
  }

  alternar(): void {
    this.tema.update((tema) => (tema === 'oscuro' ? 'claro' : 'oscuro'));
  }
}
