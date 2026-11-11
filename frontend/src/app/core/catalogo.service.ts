import { Injectable, signal } from '@angular/core';
import { ACCESORIOS, DESTACADAS, MOTOS, RECOMENDADAS_MULTIMARCA } from './datos-prueba';
import { Accesorio, ClaveMarca, Destacada, Moto } from './modelos';

@Injectable({ providedIn: 'root' })
export class CatalogoService {
  readonly motos = signal<readonly Moto[]>(MOTOS);
  readonly destacadas = signal<readonly Destacada[]>(DESTACADAS);
  readonly accesorios = signal<readonly Accesorio[]>(ACCESORIOS);

  porId(id: string): Moto | undefined {
    return this.motos().find((moto) => moto.id === id);
  }

  porMarca(marca: ClaveMarca | null): Moto[] {
    return this.motos().filter((moto) => marca === null || moto.marca === marca);
  }

  recomendadas(marca: ClaveMarca | null): Moto[] {
    if (marca === null) {
      return RECOMENDADAS_MULTIMARCA.map((id) => this.porId(id)).filter(
        (moto): moto is Moto => !!moto,
      );
    }
    return this.porMarca(marca)
      .filter((moto) => moto.recomendada)
      .slice(0, 3);
  }
}
