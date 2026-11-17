import { fotoDeMoto, slugModelo } from './fotos-motos';

describe('fotos de las motos', () => {
  it('arma el nombre del archivo igual que la lista de fotos', () => {
    expect(slugModelo('CB500 HORNET')).toBe('cb500-hornet');
    expect(slugModelo('SUPER TÉNÉRÉ 1200 ZE')).toBe('super-tenere-1200-ze');
    expect(slugModelo('FZ150 V3.0')).toBe('fz150-v3-0');
  });

  it('usa la foto de la carpeta cuando existe', () => {
    expect(fotoDeMoto('honda', 'CB500 HORNET')).toBe('/motos/honda/cb500-hornet.webp');
  });

  it('sin foto devuelve null para mostrar el dibujo', () => {
    expect(fotoDeMoto('honda', 'Moto inventada')).toBeNull();
  });

  it('si la moto trae su propia imagen se usa esa', () => {
    expect(fotoDeMoto('yamaha', 'R3', 'https://ejemplo.com/r3.webp')).toBe(
      'https://ejemplo.com/r3.webp',
    );
  });
});
