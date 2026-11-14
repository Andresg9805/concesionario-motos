import { TestBed } from '@angular/core/testing';
import { MOTOS } from './datos-prueba';
import { FiltrosService } from './filtros.service';

describe('FiltrosService', () => {
  let filtros: FiltrosService;

  beforeEach(() => {
    filtros = TestBed.inject(FiltrosService);
  });

  it('sin filtros deja todas las motos', () => {
    expect(filtros.aplicar(MOTOS)).toHaveLength(MOTOS.length);
  });

  it('el segmento A1 solo deja motos de hasta 125 cc', () => {
    filtros.segmento.set('a1');
    expect(filtros.aplicar(MOTOS).every((moto) => moto.cc <= 125)).toBe(true);
  });

  it('el rango y el precio máximo se combinan', () => {
    filtros.rango.set('r2');
    filtros.precioMaximo.set(13_000_000);
    const lista = filtros.aplicar(MOTOS);
    expect(lista.length).toBeGreaterThan(0);
    expect(lista.every((moto) => moto.precio >= 10_000_000 && moto.precio <= 13_000_000)).toBe(
      true,
    );
  });

  it('ordena por cilindraje de mayor a menor', () => {
    filtros.orden.set('cc-desc');
    const lista = filtros.ordenar(filtros.aplicar(MOTOS));
    expect(lista[0].modelo).toBe('CRF1100L Africa Twin');
  });

  it('limpiar quita los filtros', () => {
    filtros.segmento.set('a2');
    filtros.precioMaximo.set(1);
    filtros.limpiar();
    expect(filtros.aplicar(MOTOS)).toHaveLength(MOTOS.length);
  });
});
