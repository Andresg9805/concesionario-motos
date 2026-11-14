import { TestBed } from '@angular/core/testing';
import { TemaService } from './tema.service';

describe('TemaService', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
  });

  it('arranca en modo oscuro', () => {
    const tema = TestBed.inject(TemaService);
    TestBed.tick();
    expect(tema.actual()).toBe('oscuro');
    expect(document.documentElement.hasAttribute('data-theme')).toBe(false);
  });

  it('al alternar pasa a claro, lo guarda y vuelve a oscuro', () => {
    const tema = TestBed.inject(TemaService);
    tema.alternar();
    TestBed.tick();
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    expect(localStorage.getItem('cm-tema')).toBe('claro');
    tema.alternar();
    TestBed.tick();
    expect(document.documentElement.hasAttribute('data-theme')).toBe(false);
  });

  it('recuerda el modo claro guardado', () => {
    localStorage.setItem('cm-tema', 'claro');
    expect(TestBed.inject(TemaService).actual()).toBe('claro');
  });
});
