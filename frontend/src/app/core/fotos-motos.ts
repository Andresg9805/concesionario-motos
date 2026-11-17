export function fotoDeMoto(imagenUrl: string | null | undefined): string | null {
  const ruta = imagenUrl?.trim() ?? '';
  return ruta === '' ? null : ruta;
}
