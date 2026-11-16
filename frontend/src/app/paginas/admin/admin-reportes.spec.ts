import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { RadarDemandaApi, ReporteVentasApi } from '../../core/admin-api';
import { AdminReportes } from './admin-reportes';

const RADAR: RadarDemandaApi = {
  total_busquedas: 5,
  filas: [
    {
      rango: 'Menos de $300.000',
      licencia: 'A2',
      busquedas: 4,
      sin_resultados: 3,
      promedio_resultados: 0.5,
      motos_en_stock: 1,
    },
    {
      rango: '$800.000 o más',
      licencia: 'A2',
      busquedas: 1,
      sin_resultados: 0,
      promedio_resultados: 12,
      motos_en_stock: 40,
    },
  ],
};

const VENTAS: ReporteVentasApi = {
  pedidos: 2,
  ingresos_cop: 750_000,
  ticket_promedio_cop: 375_000,
  por_categoria_y_semana: [
    { categoria: 'CASCO', semana: '2026-11-16', unidades: 3, ingresos_cop: 750_000 },
  ],
  mas_vendidos: [{ nombre: 'X-Fifteen', unidades: 3, ingresos_cop: 750_000 }],
};

const SIN_VENTAS: ReporteVentasApi = {
  pedidos: 0,
  ingresos_cop: 0,
  ticket_promedio_cop: 0,
  por_categoria_y_semana: [],
  mas_vendidos: [],
};

describe('AdminReportes', () => {
  let http: HttpTestingController;

  async function abrir(radar: RadarDemandaApi, ventas: ReporteVentasApi) {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    http = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(AdminReportes);
    http.expectOne((r) => r.url.endsWith('/reportes/demanda')).flush(radar);
    http.expectOne((r) => r.url.endsWith('/reportes/ventas')).flush(ventas);
    await fixture.whenStable();
    fixture.detectChanges();
    return fixture.nativeElement as HTMLElement;
  }

  afterEach(() => http.verify());

  it('muestra el radar y marca la demanda sin atender', async () => {
    const html = await abrir(RADAR, VENTAS);
    const filas = html.querySelectorAll('tbody tr');
    expect(html.textContent).toContain('5 búsquedas registradas');
    expect(filas[0].textContent).toContain('Menos de $300.000');
    expect(filas[0].classList).toContain('bg-accentsoft');
    expect(filas[1].classList).not.toContain('bg-accentsoft');
  });

  it('muestra los totales de ventas, las categorías y los más vendidos', async () => {
    const html = await abrir(RADAR, VENTAS);
    expect(html.textContent).toContain('Cascos');
    expect(html.textContent).toContain('X-Fifteen');
    expect(html.textContent).toContain('375.000');
  });

  it('avisa cuando todavía no hay búsquedas ni ventas', async () => {
    const html = await abrir({ total_busquedas: 0, filas: [] }, SIN_VENTAS);
    expect(html.textContent).toContain('Todavía no hay búsquedas por cuota.');
    expect(html.textContent).toContain('Todavía no hay ventas pagadas.');
  });
});
