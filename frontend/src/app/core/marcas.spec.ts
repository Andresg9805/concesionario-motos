import { MARCAS, buscarMarca } from './marcas';

describe('marcas', () => {
  it('solo hay tres marcas japonesas', () => {
    expect(MARCAS.map((marca) => marca.nombre)).toEqual(['Honda', 'Kawasaki', 'Yamaha']);
  });

  it('cada marca tiene su color', () => {
    expect(buscarMarca('Honda')?.color).toBe('#CC0000');
    expect(buscarMarca('kawasaki')?.color).toBe('#69BE28');
    expect(buscarMarca(' YAMAHA ')?.color).toBe('#0055B8');
  });

  it('una marca que no vendemos no se encuentra', () => {
    expect(buscarMarca('Bajaj')).toBeUndefined();
  });
});
