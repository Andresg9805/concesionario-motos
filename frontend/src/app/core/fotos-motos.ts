import { ClaveMarca } from './modelos';

const FOTOS: Record<ClaveMarca, ReadonlySet<string>> = {
  honda: new Set([
    'africa-twin-adventure-sports',
    'cb1000-hornet-sp',
    'cb1000f',
    'cb500-hornet',
    'cb650r',
    'cb750-hornet',
    'cbr1000rr',
    'cbr1000rr-r-fireblade-sp',
    'cbr500r',
    'cbr600rr',
    'cbr650r',
    'crf1100l-africa-twin',
    'crf300l',
    'crf450rl',
    'nc750x',
    'nx500',
    'xl750-transalp',
    'xr150l',
    'xr650l',
  ]),
  kawasaki: new Set([
    'kle500-se',
    'kle650-se',
    'klx-150',
    'klx-230-df',
    'klx-230-s',
    'klx-300',
    'klx-300-df',
    'ninja-1100sx-se',
    'ninja-h2',
    'ninja-h2-carbon',
    'ninja-h2-sx-se',
    'ninja-h2r',
    'versys-1100-se',
    'versys-650',
    'versys-900-se',
    'z-h2-se',
    'z125',
    'z500',
    'z900',
    'z900-se',
  ]),
  yamaha: new Set([
    'fz150-v3-0',
    'fz25-abs',
    'mt-03',
    'mt-09',
    'mt-15',
    'r15-v4',
    'r3',
    'r7',
    'super-tenere-1200-ze',
    'tenere-700',
    'wr125r',
    'wr250f',
    'wr250r',
    'wr450f',
    'xt250',
    'xtz-125',
    'xtz-150',
    'xtz-250',
    'yzf-r1',
    'yzf-r9',
  ]),
};

export function slugModelo(modelo: string): string {
  return modelo
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function fotoDeMoto(marca: ClaveMarca, modelo: string, imagenUrl = ''): string | null {
  if (imagenUrl) {
    return imagenUrl;
  }
  const slug = slugModelo(modelo);
  return FOTOS[marca].has(slug) ? `/motos/${marca}/${slug}.webp` : null;
}
