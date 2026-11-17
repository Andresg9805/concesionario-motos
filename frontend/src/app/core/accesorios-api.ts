import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from './api.service';
import { Accesorio, IlustracionAccesorio } from './modelos';

export interface AccesorioApi {
  id: number;
  sku: string;
  nombre: string;
  categoria: string;
  fabricante: string;
  descripcion: string;
  precio_cop: number;
  stock: number;
  imagen_url: string;
}

const CATEGORIAS: Record<string, { texto: string; ilustracion: IlustracionAccesorio }> = {
  CASCO: { texto: 'Cascos', ilustracion: 'casco' },
  CHAQUETA: { texto: 'Chaquetas', ilustracion: 'chaqueta' },
  GUANTES: { texto: 'Guantes', ilustracion: 'guantes' },
  RODILLERA: { texto: 'Rodilleras', ilustracion: 'rodillera' },
  HOMBRERA: { texto: 'Hombreras', ilustracion: 'hombrera' },
  MALETA: { texto: 'Maletas', ilustracion: 'maleta' },
  MANTENIMIENTO: { texto: 'Mantenimiento', ilustracion: 'mantenimiento' },
};

export const ORDEN_CATEGORIAS = Object.values(CATEGORIAS).map((c) => c.texto);

export function textoCategoria(clave: string): string {
  const conocida = CATEGORIAS[clave];
  if (conocida) {
    return conocida.texto;
  }
  const limpia = clave.replace(/_/g, ' ').toLowerCase();
  return limpia.charAt(0).toUpperCase() + limpia.slice(1);
}

export function accesorioDesdeApi(dato: AccesorioApi): Accesorio {
  return {
    id: String(dato.id),
    categoria: textoCategoria(dato.categoria),
    nombre: dato.nombre,
    fabricante: dato.fabricante || undefined,
    descripcion: dato.descripcion,
    precio: dato.precio_cop,
    stock: dato.stock,
    ilustracion: CATEGORIAS[dato.categoria]?.ilustracion ?? 'maleta',
    imagen: dato.imagen_url?.trim() || undefined,
  };
}

@Injectable({ providedIn: 'root' })
export class AccesoriosApiService {
  private readonly api = inject(ApiService);

  listar(): Observable<Accesorio[]> {
    return this.api
      .get<AccesorioApi[]>('/accesorios')
      .pipe(map((lista) => lista.map(accesorioDesdeApi)));
  }
}
