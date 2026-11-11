import { DOCUMENT } from '@angular/common';
import { Injectable, computed, effect, inject, signal } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { MARCAS, esClaveMarca } from './marcas';
import { ClaveMarca, Marca } from './modelos';

const LLAVE = 'cm-brand';

function leerGuardada(): ClaveMarca | null {
  try {
    const guardada = localStorage.getItem(LLAVE);
    return esClaveMarca(guardada) ? guardada : null;
  } catch {
    return null;
  }
}

@Injectable({ providedIn: 'root' })
export class MarcaService {
  private readonly documento = inject(DOCUMENT);
  private readonly titulo = inject(Title);
  private readonly clave = signal<ClaveMarca | null>(leerGuardada());

  readonly actual = this.clave.asReadonly();
  readonly marca = computed<Marca | null>(() => {
    const clave = this.clave();
    return clave ? MARCAS[clave] : null;
  });

  constructor() {
    effect(() => {
      const clave = this.clave();
      const raiz = this.documento.documentElement;
      if (clave) {
        raiz.setAttribute('data-brand', clave);
      } else {
        raiz.removeAttribute('data-brand');
      }
      this.titulo.setTitle(clave ? `Candela Motors ${MARCAS[clave].nombre}` : 'Candela Motors');
      try {
        localStorage.setItem(LLAVE, clave ?? 'neutral');
      } catch {
        return;
      }
    });
  }

  elegir(clave: ClaveMarca | null): void {
    this.clave.set(clave);
  }
}
