export type ClaveMarca = 'honda' | 'kawasaki' | 'yamaha';

export interface InfoMarca {
  clave: ClaveMarca;
  nombre: string;
  color: string;
}

export const MARCAS: readonly InfoMarca[] = [
  { clave: 'honda', nombre: 'Honda', color: '#CC0000' },
  { clave: 'kawasaki', nombre: 'Kawasaki', color: '#69BE28' },
  { clave: 'yamaha', nombre: 'Yamaha', color: '#0055B8' },
];

export function buscarMarca(nombre: string): InfoMarca | undefined {
  const clave = nombre.trim().toLowerCase();
  return MARCAS.find((marca) => marca.clave === clave);
}
