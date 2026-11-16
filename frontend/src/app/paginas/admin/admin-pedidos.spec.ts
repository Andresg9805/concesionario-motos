import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { PedidoAdminApi } from '../../core/admin-api';
import { AdminPedidos } from './admin-pedidos';

const PAGADO: PedidoAdminApi = {
  id: 5,
  cliente_nombre: 'Ana Pérez',
  cliente_correo: 'ana@correo.com',
  estado: 'PAGADO',
  estado_pago: 'APROBADO',
  subtotal_cop: 350_000,
  costo_envio_cop: 12_000,
  total_cop: 362_000,
  creado_en: '2026-11-16T10:00:00-05:00',
  items: [
    {
      accesorio_id: 1,
      nombre: 'Guantes Techdura',
      cantidad: 1,
      precio_unitario_cop: 350_000,
      subtotal_cop: 350_000,
    },
  ],
  envio: { id: 9, numero_guia: 'CM-GUIA-0005', estado: 'PREPARANDO', eventos: [] },
};

const SIN_PAGAR: PedidoAdminApi = { ...PAGADO, id: 6, estado: 'PENDIENTE_PAGO', envio: null };

describe('AdminPedidos', () => {
  let http: HttpTestingController;

  async function abrir() {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    http = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(AdminPedidos);
    http.expectOne((r) => r.url.endsWith('/admin/pedidos')).flush([PAGADO, SIN_PAGAR]);
    await fixture.whenStable();
    fixture.detectChanges();
    return fixture;
  }

  afterEach(() => http.verify());

  it('arranca mostrando solo los pedidos por despachar', async () => {
    const fixture = await abrir();
    const html = fixture.nativeElement as HTMLElement;
    expect(html.textContent).toContain('Pedido #5');
    expect(html.textContent).not.toContain('Pedido #6');
  });

  it('marca el siguiente paso del envío con la nota', async () => {
    const fixture = await abrir();
    const html = fixture.nativeElement as HTMLElement;
    const boton = Array.from(html.querySelectorAll('button')).find((b) =>
      b.textContent?.includes('Marcar enviado'),
    )!;
    boton.click();
    const peticion = http.expectOne((r) => r.url.endsWith('/envios/9/estado'));
    expect(peticion.request.method).toBe('PATCH');
    expect(peticion.request.body).toEqual({ estado: 'ENVIADO', nota: '' });
    peticion.flush({ ...PAGADO.envio, estado: 'ENVIADO' });
    fixture.detectChanges();
    expect(html.textContent).toContain('Marcar en camino');
  });
});
