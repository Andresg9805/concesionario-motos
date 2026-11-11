import { ClaveMarca, Marca, Silueta, TipoMoto } from './modelos';

export const MARCAS: Record<ClaveMarca, Marca> = {
  honda: {
    clave: 'honda',
    nombre: 'Honda',
    kanji: '本田',
    origen: 'Desde 1948 · Hamamatsu',
    color: 'var(--honda)',
  },
  kawasaki: {
    clave: 'kawasaki',
    nombre: 'Kawasaki',
    kanji: '川崎',
    origen: 'Desde 1896 · Kobe',
    color: 'var(--kawasaki)',
  },
  yamaha: {
    clave: 'yamaha',
    nombre: 'Yamaha',
    kanji: 'ヤマハ',
    origen: 'Desde 1955 · Iwata',
    color: 'var(--yamaha)',
  },
};

export const LISTA_MARCAS: readonly Marca[] = Object.values(MARCAS);

export const NOMBRE_TIPO: Record<TipoMoto, string> = {
  NAKED: 'Naked',
  DOBLE_PROPOSITO: 'Doble propósito',
  TRAIL: 'Trail',
  DEPORTIVA: 'Deportiva',
};

export const SILUETA_TIPO: Record<TipoMoto, Silueta> = {
  NAKED: 'naked',
  DOBLE_PROPOSITO: 'trail',
  TRAIL: 'trail',
  DEPORTIVA: 'sport',
};

export function esClaveMarca(valor: string | null | undefined): valor is ClaveMarca {
  return valor === 'honda' || valor === 'kawasaki' || valor === 'yamaha';
}
