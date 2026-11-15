import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { AtencionAsesorApi } from '../../core/asesor-api';
import { SesionService } from '../../core/sesion.service';
import { tokenDePrueba } from '../../../testing/token';
import { PanelAsesor } from './panel-asesor';

const BASE: AtencionAsesorApi = {
  id: 1,
  codigo: 'CM-AAAA',
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

const COTIZACIONES: AtencionAsesorApi[] = [
  BASE,
  { ...BASE, id: 2, codigo: 'CM-BBBB', estado: 'NEGOCIANDO' },
  { ...BASE, id: 3, codigo: 'CM-CCCC', estado: 'VENDIDO' },
];

const COLA: AtencionAsesorApi[] = [
  {
    ...BASE,
    id: 10,
    codigo: 'TD-1111',
    tipo: 'TEST_DRIVE',
    estado: 'PENDIENTE',
    cuota_mensual_cop: null,
  },
  {
    ...BASE,
    id: 11,
    codigo: 'TD-2222',
    tipo: 'TEST_DRIVE',
    estado: 'PENDIENTE',
    cuota_mensual_cop: null,
    cliente: { nombre: 'Pedro Gil', correo: 'pedro@correo.com', celular: '3109998877' },
  },
];

describe('PanelAsesor', () => {
  let http: HttpTestingController;

  async function abrir() {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    TestBed.inject(SesionService).guardarToken(
      tokenDePrueba({ rol: 'ASESOR', nombre: 'Laura Ruiz', marca: 'honda' }),
    );
    http = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(PanelAsesor);
    http.expectOne((r) => r.url.endsWith('/asesor/atenciones')).flush(COTIZACIONES);
    http.expectOne((r) => r.url.endsWith('/asesor/test-drives')).flush(COLA);
    await fixture.whenStable();
    fixture.detectChanges();
    return fixture;
  }

  afterEach(() => http.verify());

  it('muestra el resumen y solo las cotizaciones abiertas al entrar', async () => {
    const fixture = await abrir();
    const html = fixture.nativeElement as HTMLElement;
    expect(html.textContent).toContain('Hola, Laura');
    expect(html.textContent).toContain('Asesor · Honda');
    expect(html.textContent).toContain('CM-AAAA');
    expect(html.textContent).toContain('CM-BBBB');
    expect(html.textContent).not.toContain('CM-CCCC');
  });

  it('una cotización nueva solo deja marcar contactado o descartar', async () => {
    const fixture = await abrir();
    const tarjeta = (fixture.nativeElement as HTMLElement).querySelector('li')!;
    const botones = Array.from(tarjeta.querySelectorAll('button')).map((b) =>
      b.textContent?.trim(),
    );
    expect(botones).toEqual(['Ya lo contacté', 'Descartar']);
  });

  it('al cambiar el estado actualiza la tarjeta con lo que responde el servidor', async () => {
    const fixture = await abrir();
    const html = fixture.nativeElement as HTMLElement;
    const boton = Array.from(html.querySelectorAll('button')).find((b) =>
      b.textContent?.includes('Moto vendida'),
    )!;
    boton.click();
    http
      .expectOne((r) => r.url.endsWith('/cotizaciones/2/estado'))
      .flush({ ...COTIZACIONES[1], estado: 'VENDIDO' });
    fixture.detectChanges();
    expect(html.textContent).not.toContain('CM-BBBB');
  });

  it('programa el primero de la cola y lo pasa a programados', async () => {
    const fixture = await abrir();
    const html = fixture.nativeElement as HTMLElement;
    Array.from(html.querySelectorAll<HTMLButtonElement>('[role="tab"]'))[1].click();
    fixture.detectChanges();
    expect(html.textContent).toContain('TD-1111');
    Array.from(html.querySelectorAll('button'))
      .find((b) => b.textContent?.includes('Programar'))!
      .click();
    http
      .expectOne((r) => r.url.endsWith('/asesor/test-drives/siguiente'))
      .flush({ ...COLA[0], estado: 'PROGRAMADO', fecha_programada: '2026-11-15T10:00:00' });
    fixture.detectChanges();
    const siguiente = html.querySelector('.border-accent')!;
    expect(siguiente.textContent).toContain('Pedro Gil');
    expect(html.textContent).not.toContain('Todavía no has programado');
    expect(html.textContent).toContain('TD-1111');
  });
});
