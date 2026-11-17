import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { Moto } from '../core/modelos';
import { TarjetaMoto } from './tarjeta-moto';

const CON_FOTO: Moto = {
  id: '4',
  marca: 'honda',
  modelo: 'CB500 HORNET',
  cc: 471,
  tipo: 'NAKED',
  precio: 32_990_000,
  imagen: '/motos/honda/cb500-hornet.webp',
};

const SIN_FOTO: Moto = { ...CON_FOTO, id: '99', modelo: 'Moto sin foto', imagen: undefined };

function abrir(moto: Moto): HTMLElement {
  TestBed.configureTestingModule({ providers: [provideRouter([])] });
  const fixture = TestBed.createComponent(TarjetaMoto);
  fixture.componentRef.setInput('moto', moto);
  fixture.detectChanges();
  return fixture.nativeElement as HTMLElement;
}

describe('TarjetaMoto', () => {
  it('la foto lleva a la página de la moto', () => {
    const html = abrir(CON_FOTO);
    const img = html.querySelector('img');
    expect(img?.getAttribute('src')).toBe('/motos/honda/cb500-hornet.webp');
    expect(img?.closest('a')?.getAttribute('href')).toBe('/motos/4');
  });

  it('sin foto muestra el dibujo y también lleva a la página de la moto', () => {
    const html = abrir(SIN_FOTO);
    expect(html.querySelector('img')).toBeNull();
    expect(html.querySelector('app-silueta-moto')?.closest('a')?.getAttribute('href')).toBe(
      '/motos/99',
    );
  });

  it('la tarjeta reacciona al pasar el mouse', () => {
    expect(abrir(CON_FOTO).querySelector('article')?.classList).toContain('tarjeta-hover');
  });
});
