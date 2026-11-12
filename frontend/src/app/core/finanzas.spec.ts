import {
  cuotaMensual,
  formatoCop,
  leerPesos,
  licenciaPara,
  precioMaximoPorCuota,
} from './finanzas';

describe('finanzas', () => {
  it('la cuota de la CB190R a 36 meses con 10 % de inicial es la del wireframe', () => {
    expect(cuotaMensual(12_890_000)).toBe(439_900);
  });

  it('más cuota inicial baja la cuota mensual', () => {
    expect(cuotaMensual(12_890_000, 30)).toBeLessThan(cuotaMensual(12_890_000, 10));
  });

  it('el precio máximo por cuota alcanza para una moto con esa cuota', () => {
    const maximo = precioMaximoPorCuota(450_000, 1_500_000, 36);
    expect(maximo).toBeGreaterThan(12_890_000);
    expect(maximo).toBeLessThan(15_000_000);
  });

  it('hasta 125 cc es A1 y más de 125 cc es A2', () => {
    expect(licenciaPara(124)).toBe('A1');
    expect(licenciaPara(125)).toBe('A1');
    expect(licenciaPara(126)).toBe('A2');
  });

  it('formatea pesos y los vuelve a leer', () => {
    expect(formatoCop(489_000)).toContain('489.000');
    expect(leerPesos('$ 1.500.000')).toBe(1_500_000);
    expect(leerPesos('abc')).toBe(0);
  });
});
