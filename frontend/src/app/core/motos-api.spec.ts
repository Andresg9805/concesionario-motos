import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { CatalogoService } from './catalogo.service';
import { MOTOS } from './datos-prueba';
import { MotoApi, MotosApiService, motoDesdeApi } from './motos-api';

const MOTO_API: MotoApi = {
  id: 3,
  marca: { id: 1, nombre: 'Honda', clave: 'honda', color_hex: '#CC0000' },
  modelo: 'CB190R',
  anio: 2026,
  cilindraje_cc: 184,
  tipo: 'NAKED',
  categoria_licencia: 'A2',
  precio_cop: 12890000,
  disponible: true,
  imagen_url: '',
};

describe('MotosApiService', () => {
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('convierte una moto de la API al modelo del frontend', () => {
    expect(motoDesdeApi(MOTO_API)).toEqual({
      id: '3',
      marca: 'honda',
      modelo: 'CB190R',
      cc: 184,
      tipo: 'NAKED',
      precio: 12890000,
    });
  });

  it('pide el costo real con los parámetros de uso', () => {
    TestBed.inject(MotosApiService)
      .costoReal('3', {
        km_mes: 800,
        uso: 'TRABAJO',
        cuota_inicial_cop: 1000000,
        plazo_meses: 36,
        ganancia_diaria_cop: 80000,
        dias_trabajo_mes: 24,
      })
      .subscribe();
    const pedido = http.expectOne((r) => r.url === 'http://localhost:8000/motos/3/costo-real');
    expect(pedido.request.params.get('uso')).toBe('TRABAJO');
    expect(pedido.request.params.get('dias_trabajo_mes')).toBe('24');
    pedido.flush({});
  });

  it('el catálogo usa las motos de la API cuando responde', () => {
    const catalogo = TestBed.inject(CatalogoService);
    catalogo.cargar();
    http.expectOne('http://localhost:8000/motos').flush([MOTO_API]);
    expect(catalogo.origen()).toBe('api');
    expect(catalogo.motos()).toHaveLength(1);
  });

  it('si la API falla se quedan los datos de prueba', () => {
    const catalogo = TestBed.inject(CatalogoService);
    catalogo.cargar();
    http
      .expectOne('http://localhost:8000/motos')
      .flush('sin servidor', { status: 0, statusText: 'Unknown Error' });
    expect(catalogo.origen()).toBe('prueba');
    expect(catalogo.motos()).toHaveLength(MOTOS.length);
  });
});
