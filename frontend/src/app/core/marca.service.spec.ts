import { TestBed } from '@angular/core/testing';
import { MarcaService } from './marca.service';

describe('MarcaService', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-brand');
  });

  it('empieza en la paleta neutra', () => {
    const servicio = TestBed.inject(MarcaService);
    TestBed.tick();
    expect(servicio.actual()).toBeNull();
    expect(document.documentElement.hasAttribute('data-brand')).toBe(false);
  });

  it('elegir una marca cambia data-brand en el html y la guarda', () => {
    const servicio = TestBed.inject(MarcaService);
    servicio.elegir('yamaha');
    TestBed.tick();
    expect(document.documentElement.getAttribute('data-brand')).toBe('yamaha');
    expect(localStorage.getItem('cm-brand')).toBe('yamaha');
    expect(servicio.marca()?.kanji).toBe('ヤマハ');
  });

  it('recuerda la marca guardada', () => {
    localStorage.setItem('cm-brand', 'kawasaki');
    const servicio = TestBed.inject(MarcaService);
    expect(servicio.actual()).toBe('kawasaki');
  });
});
