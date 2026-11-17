import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { CatalogoService } from '../../core/catalogo.service';
import { Accesorio } from '../../core/modelos';
import { Tienda } from './tienda';

const CON_FOTO: Accesorio = {
  id: '1',
  categoria: 'Cascos',
  nombre: 'X-Fifteen',
  fabricante: 'SHOEI',
  descripcion: 'Doble visor.',
  precio: 489000,
  stock: 12,
  ilustracion: 'casco',
  imagen: '/accesorios/sho-cas-001.webp',
};

const SIN_FOTO: Accesorio = { ...CON_FOTO, id: '2', nombre: 'Casco sin foto', imagen: undefined };

describe('Tienda', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    });
  });

  it('muestra la foto del accesorio y la ilustración cuando no tiene', async () => {
    const catalogo = TestBed.inject(CatalogoService);
    const fixture = TestBed.createComponent(Tienda);
    TestBed.inject(HttpTestingController)
      .match(() => true)
      .forEach((peticion) => peticion.flush([]));
    catalogo.accesorios.set([CON_FOTO, SIN_FOTO]);
    fixture.detectChanges();
    await fixture.whenStable();

    const pagina: HTMLElement = fixture.nativeElement;
    const foto = pagina.querySelector('img[alt="X-Fifteen"]');
    expect(foto?.getAttribute('src')).toBe('/accesorios/sho-cas-001.webp');
    expect(pagina.querySelector('img[alt="Casco sin foto"]')).toBeNull();
    expect(pagina.querySelectorAll('app-ilustracion-accesorio').length).toBe(1);
  });
});
