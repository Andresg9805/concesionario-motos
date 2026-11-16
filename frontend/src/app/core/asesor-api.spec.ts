import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import {
  AsesorApiService,
  AtencionAsesorApi,
  enlaceWhatsapp,
  fechaLocal,
  grupoDe,
  mensajeCliente,
  siguientesEstados,
} from './asesor-api';

export const COTIZACION: AtencionAsesorApi = {
  id: 7,
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
  cliente: { nombre: 'Ana Pérez', correo: 'ana@correo.com', celular: '3001234567' },
};

describe('reglas del panel del asesor', () => {
  it('solo ofrece los estados a los que se puede pasar', () => {
    expect(siguientesEstados('NUEVO')).toEqual(['CONTACTADO', 'DESCARTADO']);
    expect(siguientesEstados('NEGOCIANDO')).toEqual(['VENDIDO', 'DESCARTADO']);
    expect(siguientesEstados('VENDIDO')).toEqual([]);
    expect(siguientesEstados('DESCARTADO')).toEqual([]);
  });

  it('agrupa las cotizaciones en abiertas, vendidas y descartadas', () => {
    expect(grupoDe('NUEVO')).toBe('abiertas');
    expect(grupoDe('TEST_DRIVE')).toBe('abiertas');
    expect(grupoDe('VENDIDO')).toBe('vendidas');
    expect(grupoDe('DESCARTADO')).toBe('descartadas');
  });

  it('arma el enlace de WhatsApp con el indicativo de Colombia', () => {
    const enlace = enlaceWhatsapp('300 123 4567', 'Hola Ana');
    expect(enlace).toBe('https://wa.me/573001234567?text=Hola%20Ana');
  });

  it('el mensaje saluda al cliente y menciona la moto y el código', () => {
    const mensaje = mensajeCliente(COTIZACION, 'Laura Ruiz');
    expect(mensaje).toContain('Hola Ana');
    expect(mensaje).toContain('Honda CB190R');
    expect(mensaje).toContain('CM-4HQ8');
    expect(mensaje).toContain('cotización');
  });

  it('formatea la fecha para el campo de fecha y hora', () => {
    expect(fechaLocal(new Date(2026, 10, 5, 9, 7))).toBe('2026-11-05T09:07');
  });
});

describe('AsesorApiService', () => {
  let servicio: AsesorApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    servicio = TestBed.inject(AsesorApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('cambia el estado con PATCH', () => {
    let estado = '';
    servicio.cambiarEstado(7, 'CONTACTADO').subscribe((c) => (estado = c.estado));
    const peticion = http.expectOne((r) => r.url.endsWith('/cotizaciones/7/estado'));
    expect(peticion.request.method).toBe('PATCH');
    expect(peticion.request.body).toEqual({ estado: 'CONTACTADO' });
    peticion.flush({ ...COTIZACION, estado: 'CONTACTADO' });
    expect(estado).toBe('CONTACTADO');
  });

  it('programa el siguiente test drive de la cola', () => {
    servicio.programarSiguiente('2026-11-15T10:00').subscribe();
    const peticion = http.expectOne((r) => r.url.endsWith('/asesor/test-drives/siguiente'));
    expect(peticion.request.method).toBe('POST');
    expect(peticion.request.body).toEqual({ fecha: '2026-11-15T10:00' });
    peticion.flush({ ...COTIZACION, tipo: 'TEST_DRIVE', estado: 'PROGRAMADO' });
  });
});
