import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { AtencionApi, AtencionApiService } from './atencion-api';
import { Atencion, Moto } from './modelos';

const MOTO: Moto = {
  id: '3',
  marca: 'honda',
  modelo: 'CB190R',
  cc: 184,
  tipo: 'NAKED',
  precio: 12890000,
};

const RESPUESTA: AtencionApi = {
  codigo: 'CM-4HQ8',
  tipo: 'COTIZACION',
  estado: 'NUEVO',
  creada_en: '2026-11-13T20:00:00',
  moto: {
    id: 3,
    modelo: 'CB190R',
    marca: { id: 1, nombre: 'Honda', clave: 'honda', color_hex: '#CC0000' },
  },
  asesor: { nombre: 'Laura Ruiz', whatsapp: '3001112233' },
  cuota_mensual_cop: 439900,
};

const CONTACTO = { nombre: 'Ana', correo: 'ana@correo.com', celular: '3001234567' };

describe('AtencionApiService', () => {
  let servicio: AtencionApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    servicio = TestBed.inject(AtencionApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('envía la cotización con el crédito y devuelve el código', () => {
    let resultado: Atencion | undefined;
    servicio
      .solicitar(MOTO, 'cotizacion', CONTACTO, { cuota_inicial_cop: 1289000, plazo_meses: 36 })
      .subscribe((a) => (resultado = a));
    const pedido = http.expectOne('http://localhost:8000/cotizaciones');
    expect(pedido.request.body).toEqual({
      moto_id: 3,
      ...CONTACTO,
      acepta_contacto: true,
      cuota_inicial_cop: 1289000,
      plazo_meses: 36,
    });
    pedido.flush(RESPUESTA);
    expect(resultado?.codigo).toBe('CM-4HQ8');
    expect(resultado?.asesor.nombre).toBe('Laura Ruiz');
  });

  it('el test drive va a su propia ruta y sin crédito', () => {
    servicio.solicitar(MOTO, 'testdrive', CONTACTO, null).subscribe();
    const pedido = http.expectOne('http://localhost:8000/test-drives');
    expect(pedido.request.body.plazo_meses).toBeUndefined();
    pedido.flush({ ...RESPUESTA, tipo: 'TEST_DRIVE', estado: 'PENDIENTE' });
  });

  it('si el servidor no está, registra la atención en el navegador', () => {
    let resultado: Atencion | undefined;
    servicio.solicitar(MOTO, 'cotizacion', CONTACTO, null).subscribe((a) => (resultado = a));
    http
      .expectOne('http://localhost:8000/cotizaciones')
      .flush('', { status: 0, statusText: 'Unknown Error' });
    expect(resultado?.codigo).toMatch(/^CM-[A-Z0-9]{4}$/);
  });

  it('un error de datos no se esconde', () => {
    let fallo = false;
    servicio
      .solicitar(MOTO, 'cotizacion', CONTACTO, null)
      .subscribe({ error: () => (fallo = true) });
    http
      .expectOne('http://localhost:8000/cotizaciones')
      .flush({}, { status: 422, statusText: 'Unprocessable Entity' });
    expect(fallo).toBe(true);
  });

  it('el seguimiento consulta la API y si no hay servidor usa el código de ejemplo', () => {
    let encontrada: Atencion | undefined;
    servicio.buscar('cm-7k2q').subscribe((a) => (encontrada = a));
    http
      .expectOne('http://localhost:8000/seguimiento/CM-7K2Q')
      .flush('', { status: 0, statusText: 'Unknown Error' });
    expect(encontrada?.estado).toBe('CONTACTADO');
  });
});
