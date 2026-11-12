import { TestBed } from '@angular/core/testing';
import { CatalogoService } from './catalogo.service';
import { NOMBRE_TIPO } from './marcas';

describe('CatalogoService', () => {
  let catalogo: CatalogoService;

  beforeEach(() => {
    catalogo = TestBed.inject(CatalogoService);
  });

  it('solo hay motos de los cuatro tipos que decidimos', () => {
    const tipos = new Set(catalogo.motos().map((moto) => moto.tipo));
    expect([...tipos].every((tipo) => tipo in NOMBRE_TIPO)).toBe(true);
    expect(catalogo.motos().some((moto) => /scooter|nmax|pcx|navi|bws/i.test(moto.modelo))).toBe(
      false,
    );
  });

  it('cuenta los modelos por marca', () => {
    expect(catalogo.porMarca(null)).toHaveLength(24);
    expect(catalogo.porMarca('honda')).toHaveLength(8);
    expect(catalogo.porMarca('kawasaki')).toHaveLength(8);
    expect(catalogo.porMarca('yamaha')).toHaveLength(8);
  });

  it('sin marca recomienda una de cada marca', () => {
    expect(catalogo.recomendadas(null).map((moto) => moto.marca)).toEqual([
      'honda',
      'kawasaki',
      'yamaha',
    ]);
  });

  it('con marca recomienda tres de esa marca', () => {
    const lista = catalogo.recomendadas('kawasaki');
    expect(lista).toHaveLength(3);
    expect(lista.every((moto) => moto.marca === 'kawasaki')).toBe(true);
  });
});
