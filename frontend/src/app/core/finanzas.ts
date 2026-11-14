import { CategoriaLicencia } from './modelos';

export const TASA_MENSUAL = 0.0179;
export const CILINDRAJE_MAXIMO_A1 = 125;

export function cuotaMensual(precio: number, inicialPct = 10, meses = 36): number {
  const financiado = precio * (1 - inicialPct / 100);
  const cuota = (financiado * TASA_MENSUAL) / (1 - Math.pow(1 + TASA_MENSUAL, -meses));
  return Math.round(cuota / 100) * 100;
}

export function precioMaximoPorCuota(cuota: number, inicial: number, meses: number): number {
  return Math.floor((cuota * (1 - Math.pow(1 + TASA_MENSUAL, -meses))) / TASA_MENSUAL + inicial);
}

export function licenciaPara(cc: number): CategoriaLicencia {
  return cc <= CILINDRAJE_MAXIMO_A1 ? 'A1' : 'A2';
}

const FORMATO_COP = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
});

export function formatoCop(valor: number): string {
  return FORMATO_COP.format(valor).replace(/\s/g, ' ');
}

export function leerPesos(texto: string): number {
  return parseInt(texto.replace(/\D/g, ''), 10) || 0;
}
