import { TestBed } from '@angular/core/testing';
import { MarcaService } from '../../../core/marca.service';
import { BANNERS, Portada } from './portada';

describe('Portada', () => {
  function abrir() {
    localStorage.clear();
    const fixture = TestBed.createComponent(Portada);
    fixture.detectChanges();
    return fixture;
  }

  it('muestra las tres imágenes de las marcas en el carrusel', () => {
    const html = abrir().nativeElement as HTMLElement;
    const imagenes = [...html.querySelectorAll('img')].map((img) => img.getAttribute('src'));
    expect(imagenes).toEqual(BANNERS.map((b) => b.src));
    expect(html.querySelectorAll('[role=tab]').length).toBe(3);
  });

  it('al hacer clic en una imagen elige esa marca', () => {
    const fixture = abrir();
    const html = fixture.nativeElement as HTMLElement;
    const kawasaki = html.querySelector<HTMLButtonElement>('[aria-label="Ver motos Kawasaki"]')!;
    kawasaki.click();
    expect(TestBed.inject(MarcaService).actual()).toBe('kawasaki');
  });
});
