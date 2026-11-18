import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { FiltrosService } from '../../../core/filtros.service';
import { precioMaximoPorCuota } from '../../../core/finanzas';
import { Cotizar } from './cotizar';

interface ConAcceso {
  cuota: string;
  inicial: string;
  plazo: number;
  licencia: 'A1' | 'A2';
  buscarPorCuota(): void;
}

describe('Buscar por cuota', () => {
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    });
    http = TestBed.inject(HttpTestingController);
  });

  function buscar(): ConAcceso {
    const componente = TestBed.createComponent(Cotizar).componentInstance as unknown as ConAcceso;
    componente.cuota = '1.300.000';
    componente.inicial = '5.000.000';
    componente.plazo = 36;
    componente.licencia = 'A2';
    componente.buscarPorCuota();
    return componente;
  }

  it('consulta la API y la siguiente búsqueda manda la misma sesión', () => {
    buscar();
    const primera = http.expectOne((r) => r.url === 'http://localhost:8000/motos/por-cuota');
    expect(primera.request.params.get('cuota_maxima_cop')).toBe('1300000');
    expect(primera.request.params.get('licencia')).toBe('A2');
    expect(primera.request.headers.has('X-Sesion-Id')).toBe(false);
    primera.flush({
      busqueda_id: 1,
      sesion_id: 'sesion-de-prueba',
      simulaciones_en_sesion: 1,
      precio_maximo_cop: 39_000_000,
      cantidad_resultados: 0,
      motos: [],
    });
    expect(TestBed.inject(FiltrosService).precioMaximo()).toBe(39_000_000);

    buscar();
    const segunda = http.expectOne((r) => r.url === 'http://localhost:8000/motos/por-cuota');
    expect(segunda.request.headers.get('X-Sesion-Id')).toBe('sesion-de-prueba');
  });

  it('si la API no responde calcula el precio máximo en el navegador', () => {
    buscar();
    http
      .expectOne((r) => r.url === 'http://localhost:8000/motos/por-cuota')
      .flush('', { status: 0, statusText: 'Unknown Error' });
    expect(TestBed.inject(FiltrosService).precioMaximo()).toBe(
      precioMaximoPorCuota(1_300_000, 5_000_000, 36),
    );
  });
});
