import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { firstValueFrom } from 'rxjs';
import { tokenDePrueba } from '../../testing/token';
import { AuthService } from './auth.service';
import { SesionService } from './sesion.service';

describe('AuthService', () => {
  let auth: AuthService;
  let http: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    auth = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('al ingresar manda solo correo y contraseña, y el rol sale del token', async () => {
    const respuesta = firstValueFrom(auth.ingresar('asesor@candela.co', 'clave1234'));
    const peticion = http.expectOne('http://localhost:8000/auth/login');
    expect(peticion.request.body).toEqual({ correo: 'asesor@candela.co', contrasena: 'clave1234' });
    peticion.flush({
      access_token: tokenDePrueba({ nombre: 'Santiago Mejía', rol: 'ASESOR', marca: 'kawasaki' }),
      token_type: 'bearer',
    });
    const usuario = await respuesta;
    expect(usuario.rol).toBe('ASESOR');
    expect(TestBed.inject(SesionService).rol()).toBe('ASESOR');
  });

  it('con credenciales malas muestra un mensaje claro', async () => {
    const respuesta = firstValueFrom(auth.ingresar('x@y.co', 'mala'));
    http
      .expectOne('http://localhost:8000/auth/login')
      .flush({}, { status: 401, statusText: 'Unauthorized' });
    await expect(respuesta).rejects.toThrow('Correo o contraseña incorrectos.');
  });

  it('si el servidor no responde lo dice', async () => {
    const respuesta = firstValueFrom(auth.ingresar('x@y.co', 'clave1234'));
    http
      .expectOne('http://localhost:8000/auth/login')
      .error(new ProgressEvent('error'), { status: 0 });
    await expect(respuesta).rejects.toThrow('No pudimos conectar con el servidor');
  });

  it('el registro no manda rol y avisa si el correo ya existe', async () => {
    const respuesta = firstValueFrom(
      auth.registrar({
        nombre: 'Ana',
        correo: 'ana@correo.co',
        celular: '3001234567',
        contrasena: 'clave1234',
      }),
    );
    const peticion = http.expectOne('http://localhost:8000/auth/registro');
    expect(peticion.request.body.rol).toBeUndefined();
    peticion.flush({}, { status: 409, statusText: 'Conflict' });
    await expect(respuesta).rejects.toThrow('Ya existe una cuenta con ese correo.');
  });
});
