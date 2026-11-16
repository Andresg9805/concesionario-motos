import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { SesionService } from '../../core/sesion.service';
import { tokenDePrueba } from '../../../testing/token';
import { Cuenta } from './cuenta';

const PEDIDO = {
  pedido_id: 7,
  estado_pago: 'APROBADO',
  estado_pedido: 'PAGADO',
  total_cop: 3_012_000,
  numero_guia: 'CM-GUIA-0007',
  reservado_hasta: null,
  subtotal_cop: 3_000_000,
  costo_envio_cop: 12_000,
  creado_en: '2026-11-16T10:00:00-05:00',
};

const COTIZACION = {
  codigo: 'CM-4HQ8',
  tipo: 'COTIZACION',
  estado: 'CONTACTADO',
  creada_en: '2026-11-15T20:00:00-05:00',
  moto: {
    id: 3,
    modelo: 'CB190R',
    marca: { id: 1, nombre: 'Honda', clave: 'honda', color_hex: '#CC0000' },
  },
  asesor: { nombre: 'Laura Ruiz', whatsapp: '3001112233' },
  cuota_mensual_cop: 439_900,
};

describe('Cuenta', () => {
  let http: HttpTestingController;

  async function abrir() {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    TestBed.inject(SesionService).guardarToken(
      tokenDePrueba({ rol: 'CLIENTE', nombre: 'Ana Pérez', marca: null }),
    );
    http = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(Cuenta);
    http.expectOne((r) => r.url.endsWith('/mis-pedidos')).flush([PEDIDO]);
    http.expectOne((r) => r.url.endsWith('/mis-cotizaciones')).flush([COTIZACION]);
    http.expectOne((r) => r.url.endsWith('/mis-direcciones')).flush([]);
    await fixture.whenStable();
    fixture.detectChanges();
    return fixture;
  }

  afterEach(() => http.verify());

  it('saluda al cliente y muestra sus pedidos', async () => {
    const fixture = await abrir();
    const html = fixture.nativeElement as HTMLElement;
    expect(html.textContent).toContain('Hola, Ana');
    expect(html.textContent).toContain('Pedido #7');
    expect(html.textContent).toContain('CM-GUIA-0007');
    expect(html.textContent).toContain('Pagado');
  });

  it('al abrir el detalle muestra los productos y el avance del envío', async () => {
    const fixture = await abrir();
    const html = fixture.nativeElement as HTMLElement;
    Array.from(html.querySelectorAll('button'))
      .find((b) => b.textContent?.includes('Ver detalle'))!
      .click();
    http
      .expectOne((r) => r.url.endsWith('/mis-pedidos/7'))
      .flush({
        ...PEDIDO,
        items: [
          {
            accesorio_id: 1,
            nombre: 'X-Fifteen',
            cantidad: 1,
            precio_unitario_cop: 3_000_000,
            subtotal_cop: 3_000_000,
          },
        ],
        estado_envio: 'ENVIADO',
        eventos: [
          { estado: 'PREPARANDO', fecha: '2026-11-16T10:00:00-05:00', nota: 'Pago aprobado' },
          { estado: 'ENVIADO', fecha: '2026-11-16T15:00:00-05:00', nota: '' },
        ],
      });
    fixture.detectChanges();
    expect(html.textContent).toContain('1 × X-Fifteen');
    expect(html.querySelectorAll('ol[aria-label="Seguimiento del envío"] li').length).toBe(4);
  });

  it('en cotizaciones muestra la moto, el estado y el asesor', async () => {
    const fixture = await abrir();
    const html = fixture.nativeElement as HTMLElement;
    Array.from(html.querySelectorAll<HTMLButtonElement>('[role="tab"]'))[1].click();
    fixture.detectChanges();
    expect(html.textContent).toContain('Honda CB190R');
    expect(html.textContent).toContain('El asesor te contactó');
    expect(html.textContent).toContain('Laura Ruiz');
  });
});
