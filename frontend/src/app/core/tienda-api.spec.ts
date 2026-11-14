import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { DEPARTAMENTOS_RESPALDO, TiendaApiService } from './tienda-api';

describe('TiendaApiService', () => {
  let tienda: TiendaApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    tienda = TestBed.inject(TiendaApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('tiene los 33 departamentos de respaldo con su costo de envío', () => {
    expect(DEPARTAMENTOS_RESPALDO).toHaveLength(33);
    expect(DEPARTAMENTOS_RESPALDO.find((d) => d.codigo === '11')?.dias_envio).toBe(1);
  });

  it('si la API no responde usa los departamentos de respaldo', () => {
    let respaldo = false;
    tienda.departamentos().subscribe((r) => (respaldo = r.respaldo));
    http
      .expectOne('http://localhost:8000/departamentos')
      .flush('', { status: 0, statusText: 'Unknown Error' });
    expect(respaldo).toBe(true);
  });

  it('crea la dirección y luego el pedido', () => {
    tienda
      .crearPedido(
        {
          nombre_recibe: 'Ana',
          telefono: '3001234567',
          departamento_codigo: '11',
          municipio_codigo: '11001',
          municipio_nombre: 'Bogotá',
          direccion: 'Calle 1 # 2-3',
          detalle: '',
        },
        [{ accesorio_id: '7', cantidad: 2 }],
      )
      .subscribe();
    http.expectOne('http://localhost:8000/mis-direcciones').flush({ id: 5 });
    const pedido = http.expectOne('http://localhost:8000/pedidos');
    expect(pedido.request.body).toEqual({
      direccion_id: 5,
      items: [{ accesorio_id: '7', cantidad: 2 }],
    });
    pedido.flush({});
  });
});
