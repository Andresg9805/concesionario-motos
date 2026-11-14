export type ClaveMarca = 'honda' | 'kawasaki' | 'yamaha';

export type TipoMoto = 'NAKED' | 'DOBLE_PROPOSITO' | 'TRAIL' | 'DEPORTIVA';

export type Silueta = 'naked' | 'trail' | 'doble' | 'sport';

export type CategoriaLicencia = 'A1' | 'A2';

export interface Marca {
  clave: ClaveMarca;
  nombre: string;
  kanji: string;
  origen: string;
  color: string;
}

export interface Moto {
  id: string;
  marca: ClaveMarca;
  modelo: string;
  cc: number;
  tipo: TipoMoto;
  precio: number;
  recomendada?: boolean;
}

export interface Destacada {
  motoId: string;
  frase: string;
}

export type CategoriaAccesorio =
  'Cascos' | 'Chaquetas' | 'Guantes' | 'Rodilleras' | 'Hombreras' | 'Maletas' | 'Mantenimiento';

export type IlustracionAccesorio =
  'casco' | 'chaqueta' | 'guantes' | 'rodillera' | 'hombrera' | 'maleta' | 'mantenimiento';

export interface Accesorio {
  id: string;
  categoria: CategoriaAccesorio;
  nombre: string;
  descripcion: string;
  precio: number;
  stock: number;
  ilustracion: IlustracionAccesorio;
}

export interface Asesor {
  nombre: string;
  whatsapp: string;
  abiertas: number;
}

export type TipoAtencion = 'cotizacion' | 'testdrive';

export interface Atencion {
  codigo: string;
  tipo: TipoAtencion;
  estado: string;
  asesor: Asesor;
  marca: ClaveMarca;
  moto: string;
  ejemplo?: boolean;
}
