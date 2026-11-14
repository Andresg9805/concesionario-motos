import { TestBed } from '@angular/core/testing';
import { tokenDePrueba } from '../../testing/token';
import { SesionService, leerUsuario } from './sesion.service';

describe('SesionService', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('lee el nombre, el rol y la marca del token', () => {
    const usuario = leerUsuario(
      tokenDePrueba({ sub: '7', nombre: 'Daniela Pardo', rol: 'ASESOR', marca: 'yamaha' }),
    );
    expect(usuario).toMatchObject({
      id: '7',
      nombre: 'Daniela Pardo',
      rol: 'ASESOR',
      marca: 'yamaha',
    });
  });

  it('un token vencido, dañado o con un rol que no existe no sirve', () => {
    expect(leerUsuario(tokenDePrueba({ rol: 'CLIENTE' }, -10))).toBeNull();
    expect(leerUsuario('no-es-un-token')).toBeNull();
    expect(leerUsuario(tokenDePrueba({ rol: 'SUPERUSUARIO' }))).toBeNull();
  });

  it('sin token no está autenticado', () => {
    const sesion = TestBed.inject(SesionService);
    expect(sesion.autenticado()).toBe(false);
    expect(sesion.rol()).toBeNull();
  });

  it('guarda un token válido y lo deja en localStorage', () => {
    const sesion = TestBed.inject(SesionService);
    const token = tokenDePrueba({ nombre: 'Andrés', rol: 'CLIENTE' });
    expect(sesion.guardarToken(token)?.rol).toBe('CLIENTE');
    expect(sesion.autenticado()).toBe(true);
    expect(localStorage.getItem('candela_token')).toBe(token);
  });

  it('no guarda un token que no se puede leer', () => {
    const sesion = TestBed.inject(SesionService);
    expect(sesion.guardarToken('basura')).toBeNull();
    expect(sesion.autenticado()).toBe(false);
  });

  it('cerrar sesión borra el token', () => {
    const sesion = TestBed.inject(SesionService);
    sesion.guardarToken(tokenDePrueba({ rol: 'ADMIN' }));
    sesion.cerrarSesion();
    expect(sesion.token()).toBeNull();
    expect(localStorage.getItem('candela_token')).toBeNull();
  });
});
