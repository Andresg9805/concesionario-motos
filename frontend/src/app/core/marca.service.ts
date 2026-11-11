import { DOCUMENT } from '@angular/common';
import { Injectable, computed, effect, inject, signal } from '@angular/core';
import { ClaveMarca, InfoMarca, MARCAS } from './marcas';

@Injectable({ providedIn: 'root' })
export class MarcaService {
  private readonly documento = inject(DOCUMENT);
  private readonly claveActual = signal<ClaveMarca | null>(null);

  readonly actual = computed<InfoMarca | null>(
    () => MARCAS.find((marca) => marca.clave === this.claveActual()) ?? null,
  );

  constructor() {
    effect(() => {
      const clave = this.claveActual();
      const body = this.documento.body;
      if (clave) {
        body.setAttribute('data-marca', clave);
      } else {
        body.removeAttribute('data-marca');
      }
    });
  }

  elegir(clave: ClaveMarca | null): void {
    this.claveActual.set(clave);
  }

  alternar(clave: ClaveMarca): void {
    this.claveActual.update((actual) => (actual === clave ? null : clave));
  }
}
