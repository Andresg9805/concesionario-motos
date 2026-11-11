import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { UiService } from '../core/ui.service';
import { AccesoDialogo } from './acceso-dialogo';

describe('AccesoDialogo', () => {
  it('el inicio de sesión solo pide correo y contraseña, sin elegir rol', async () => {
    HTMLDialogElement.prototype.showModal ??= function (this: HTMLDialogElement) {
      this.setAttribute('open', '');
    };
    TestBed.configureTestingModule({ providers: [provideRouter([]), provideHttpClient()] });
    const fixture = TestBed.createComponent(AccesoDialogo);
    TestBed.inject(UiService).accesoAbierto.set(true);
    await fixture.whenStable();
    fixture.detectChanges();
    const html = fixture.nativeElement as HTMLElement;
    expect(html.querySelector('#correoIngreso')).not.toBeNull();
    expect(html.querySelector('#claveIngreso')).not.toBeNull();
    expect(html.querySelector('[role="radiogroup"]')).toBeNull();
    expect(html.textContent).not.toContain('Ingresar como');
    expect(html.textContent).not.toContain('Administrador');
    expect(html.textContent).not.toContain('Marca de especialidad');
  });
});
