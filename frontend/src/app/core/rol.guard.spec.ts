import { TestBed } from '@angular/core/testing';
import {
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
  UrlTree,
  provideRouter,
} from '@angular/router';
import { tokenDePrueba } from '../../testing/token';
import { soloRol } from './rol.guard';
import { SesionService } from './sesion.service';
import { UiService } from './ui.service';

describe('soloRol', () => {
  function revisar(rol: 'ASESOR' | 'ADMIN') {
    return TestBed.runInInjectionContext(() =>
      soloRol(rol)({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    );
  }

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({ providers: [provideRouter([])] });
  });

  it('deja pasar al asesor a su panel', () => {
    TestBed.inject(SesionService).guardarToken(tokenDePrueba({ rol: 'ASESOR' }));
    expect(revisar('ASESOR')).toBe(true);
  });

  it('un cliente no entra al panel de administración aunque escriba la URL', () => {
    TestBed.inject(SesionService).guardarToken(tokenDePrueba({ rol: 'CLIENTE' }));
    expect(revisar('ADMIN')).toBeInstanceOf(UrlTree);
  });

  it('sin sesión manda al inicio y abre el inicio de sesión', () => {
    expect(revisar('ADMIN')).toBeInstanceOf(UrlTree);
    expect(TestBed.inject(UiService).accesoAbierto()).toBe(true);
  });
});
