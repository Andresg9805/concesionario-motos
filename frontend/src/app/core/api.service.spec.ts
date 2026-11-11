import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ApiService } from './api.service';
import { authInterceptor } from './auth.interceptor';
import { tokenDePrueba } from '../../testing/token';
import { SesionService } from './sesion.service';

describe('ApiService', () => {
  let api: ApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
      ],
    });
    api = TestBed.inject(ApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('arma la url con la base de la API', () => {
    expect(api.url('motos')).toBe('http://localhost:8000/motos');
    expect(api.url('/motos')).toBe('http://localhost:8000/motos');
  });

  it('manda los filtros como parámetros y quita los vacíos', () => {
    api.get('/motos', { marca: 'honda', cuota_max: 500000, tipo: '', licencia: null }).subscribe();
    const peticion = http.expectOne((p) => p.url === 'http://localhost:8000/motos');
    expect(peticion.request.params.get('marca')).toBe('honda');
    expect(peticion.request.params.get('cuota_max')).toBe('500000');
    expect(peticion.request.params.has('tipo')).toBe(false);
    expect(peticion.request.params.has('licencia')).toBe(false);
    peticion.flush([]);
  });

  it('el post manda el cuerpo', () => {
    api.post('/cotizaciones', { moto_id: 1 }).subscribe();
    const peticion = http.expectOne('http://localhost:8000/cotizaciones');
    expect(peticion.request.method).toBe('POST');
    expect(peticion.request.body).toEqual({ moto_id: 1 });
    peticion.flush({});
  });

  it('sin sesión no manda el token', () => {
    api.get('/motos').subscribe();
    const peticion = http.expectOne('http://localhost:8000/motos');
    expect(peticion.request.headers.has('Authorization')).toBe(false);
    peticion.flush([]);
  });

  it('con sesión manda el token JWT', () => {
    const token = tokenDePrueba({ rol: 'CLIENTE' });
    TestBed.inject(SesionService).guardarToken(token);
    api.get('/mis-pedidos').subscribe();
    const peticion = http.expectOne('http://localhost:8000/mis-pedidos');
    expect(peticion.request.headers.get('Authorization')).toBe(`Bearer ${token}`);
    peticion.flush([]);
  });
});
