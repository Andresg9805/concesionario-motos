import { TestBed } from '@angular/core/testing';
import { SesionService } from './sesion.service';

describe('SesionService', () => {
  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({});
  });

  it('sin token no está autenticado', () => {
    const sesion = TestBed.inject(SesionService);
    expect(sesion.autenticado()).toBe(false);
  });

  it('guarda el token y lo deja en localStorage', () => {
    const sesion = TestBed.inject(SesionService);
    sesion.guardarToken('abc');
    expect(sesion.autenticado()).toBe(true);
    expect(localStorage.getItem('candela_token')).toBe('abc');
  });

  it('cerrar sesión borra el token', () => {
    const sesion = TestBed.inject(SesionService);
    sesion.guardarToken('abc');
    sesion.cerrarSesion();
    expect(sesion.token()).toBeNull();
    expect(localStorage.getItem('candela_token')).toBeNull();
  });
});
