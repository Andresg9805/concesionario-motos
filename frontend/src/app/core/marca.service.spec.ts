import { TestBed } from '@angular/core/testing';
import { MarcaService } from './marca.service';

describe('MarcaService', () => {
  let servicio: MarcaService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    servicio = TestBed.inject(MarcaService);
  });

  afterEach(() => {
    document.body.removeAttribute('data-marca');
  });

  it('empieza sin marca elegida', () => {
    expect(servicio.actual()).toBeNull();
  });

  it('al elegir una marca la pone en el body para cambiar los colores', () => {
    servicio.elegir('kawasaki');
    TestBed.tick();
    expect(servicio.actual()?.nombre).toBe('Kawasaki');
    expect(document.body.getAttribute('data-marca')).toBe('kawasaki');
  });

  it('alternar la misma marca la quita', () => {
    servicio.alternar('yamaha');
    servicio.alternar('yamaha');
    TestBed.tick();
    expect(servicio.actual()).toBeNull();
    expect(document.body.hasAttribute('data-marca')).toBe(false);
  });
});
