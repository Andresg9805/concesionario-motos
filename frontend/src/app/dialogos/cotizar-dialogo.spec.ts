import { TestBed } from '@angular/core/testing';
import { MOTOS } from '../core/datos-prueba';
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
    return fixture.nativeElement as HTMLElement;
  }

  it('la cotización muestra la financiación', async () => {
    const html = await abrir('cotizacion');
    expect(html.textContent).toContain('Cuota mensual estimada');
    expect(html.querySelector('#qPlazo')).not.toBeNull();
  });

  it('el test drive no muestra precio, cuota inicial, plazo ni cuota', async () => {
    const html = await abrir('testdrive');
    expect(html.textContent).not.toContain('Cuota mensual estimada');
    expect(html.textContent).not.toContain('9.590.000');
    expect(html.querySelector('#qInicial')).toBeNull();
    expect(html.querySelector('#qPlazo')).toBeNull();
    expect(html.textContent).toContain('Pedir test drive');
  });
});
