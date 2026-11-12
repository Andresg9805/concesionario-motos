import { Injectable, signal } from '@angular/core';
import { ASESORES } from './datos-prueba';
import { Asesor, Atencion, ClaveMarca, Moto, TipoAtencion } from './modelos';

export const ALFABETO_CODIGO = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
export const FORMATO_CODIGO = /^CM-[A-Z0-9]{4}$/;

export const PASOS_COTIZACION = ['NUEVO', 'CONTACTADO', 'TEST_DRIVE', 'NEGOCIANDO', 'VENDIDO'];
export const PASOS_TEST_DRIVE = ['PENDIENTE', 'PROGRAMADO', 'REALIZADO'];

const EJEMPLO: Atencion = {
  codigo: 'CM-7K2Q',
  tipo: 'cotizacion',
  estado: 'CONTACTADO',
  asesor: ASESORES.honda[1],
  marca: 'honda',
  moto: 'CB190R',
  ejemplo: true,
};

@Injectable({ providedIn: 'root' })
export class AtencionService {
  private readonly atenciones = signal(new Map<string, Atencion>([[EJEMPLO.codigo, EJEMPLO]]));

  generarCodigo(azar: () => number = Math.random): string {
    let codigo = '';
    do {
      codigo = 'CM-';
      for (let i = 0; i < 4; i++) {
        codigo += ALFABETO_CODIGO[Math.floor(azar() * ALFABETO_CODIGO.length)];
      }
    } while (this.atenciones().has(codigo));
    return codigo;
  }

  elegirAsesor(marca: ClaveMarca): Asesor {
    return [...ASESORES[marca]].sort((a, b) => a.abiertas - b.abiertas)[0];
  }

  registrar(moto: Moto, tipo: TipoAtencion): Atencion {
    const asesor = this.elegirAsesor(moto.marca);
    asesor.abiertas++;
    const atencion: Atencion = {
      codigo: this.generarCodigo(),
      tipo,
      estado: tipo === 'testdrive' ? 'PENDIENTE' : 'NUEVO',
      asesor,
      marca: moto.marca,
      moto: moto.modelo,
    };
    this.atenciones.update((mapa) => new Map(mapa).set(atencion.codigo, atencion));
    return atencion;
  }

  consultar(codigo: string): Atencion | undefined {
    return this.atenciones().get(codigo.trim().toUpperCase());
  }
}
