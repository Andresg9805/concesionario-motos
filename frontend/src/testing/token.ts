function base64Url(texto: string): string {
  const bytes = new TextEncoder().encode(texto);
  let binario = '';
  bytes.forEach((b) => (binario += String.fromCharCode(b)));
  return btoa(binario).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

export function tokenDePrueba(datos: Record<string, unknown>, segundos = 3600): string {
  const cabecera = base64Url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const cuerpo = base64Url(
    JSON.stringify({ exp: Math.floor(Date.now() / 1000) + segundos, ...datos }),
  );
  return `${cabecera}.${cuerpo}.firma`;
}
