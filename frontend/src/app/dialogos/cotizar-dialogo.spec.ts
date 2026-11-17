import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { MOTOS } from '../core/datos-prueba';
import { SesionService } from '../core/sesion.service';
import { UiService } from '../core/ui.service';
import { CotizarDialogo } from './cotizar-dialogo';

describe('CotizarDialogo', () => {
  const moto = MOTOS.find((m) => m.id === 'y-xtz125')!;

  async function abrir(tipo: 'cotizacion' | 'testdrive') {
    HTMLDialogElement.prototype.showModal ??= function (this: HTMLDialogElement) {
      this.setAttribute('open', '');
    };
    const fixture = TestBed.createComponent(CotizarDialogo);
    TestBed.inject(UiService).abrirCotizacion(moto, tipo);
    await fixture.whenStable();
    fixture.detectChanges();
    return fixture;
  }

  it('la cotización muestra la financiación', async () => {
    const html = (await abrir('cotizacion')).nativeElement as HTMLElement;
    expect(html.textContent).toContain('Cuota mensual estimada');
    expect(html.querySelector('#qPlazo')).not.toBeNull();
  });

  it('el test drive no muestra precio, cuota inicial, plazo ni cuota', async () => {
    const html = (await abrir('testdrive')).nativeElement as HTMLElement;
    expect(html.textContent).not.toContain('Cuota mensual estimada');
    expect(html.textContent).not.toContain('9.590.000');
    expect(html.querySelector('#qInicial')).toBeNull();
    expect(html.querySelector('#qPlazo')).toBeNull();
    expect(html.textContent).toContain('Pedir test drive');
  });

  it('con la sesión de un cliente llena nombre, correo y celular con los datos de la cuenta', async () => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    const parte = (datos: object) => btoa(JSON.stringify(datos)).replace(/=+$/, '');
    const exp = Math.floor(Date.now() / 1000) + 3600;
    TestBed.inject(SesionService).guardarToken(
      `${parte({ alg: 'HS256' })}.${parte({ sub: '7', nombre: 'Ana Pérez', rol: 'CLIENTE', exp })}.firma`,
    );
    const http = TestBed.inject(HttpTestingController);

    const fixture = await abrir('testdrive');
    http
      .expectOne((r) => r.url.endsWith('/auth/yo'))
      .flush({
        id: 7,
        nombre: 'Ana Pérez',
        rol: 'CLIENTE',
        correo: 'ana@correo.com',
        celular: '3001234567',
      });
    await fixture.whenStable();
    fixture.detectChanges();
    await fixture.whenStable();
    const html = fixture.nativeElement as HTMLElement;
    const valores = [...html.querySelectorAll('input')].map((i) => (i as HTMLInputElement).value);
    expect(valores).toContain('Ana Pérez');
    expect(valores).toContain('ana@correo.com');
    expect(valores).toContain('3001234567');
    http.verify();
    localStorage.clear();
  });
});
