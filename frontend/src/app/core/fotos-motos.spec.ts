import { fotoDeMoto } from './fotos-motos';

describe('fotos de las motos', () => {
  it('usa la imagen que viene de la base de datos', () => {
    expect(fotoDeMoto('/motos/yamaha/r3.webp')).toBe('/motos/yamaha/r3.webp');
  });

  it('también sirve con una imagen externa que ponga el administrador', () => {
    expect(fotoDeMoto('https://ejemplo.com/r3.webp')).toBe('https://ejemplo.com/r3.webp');
  });

  it('sin imagen devuelve null para mostrar el dibujo', () => {
    expect(fotoDeMoto('')).toBeNull();
    expect(fotoDeMoto('   ')).toBeNull();
    expect(fotoDeMoto(undefined)).toBeNull();
  });
});
