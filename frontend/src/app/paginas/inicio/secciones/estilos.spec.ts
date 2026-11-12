import { TestBed } from '@angular/core/testing';
import { MOTOS } from '../../../core/datos-prueba';
import { FiltrosService } from '../../../core/filtros.service';
import { MarcaService } from '../../../core/marca.service';
import { Estilos } from './estilos';

describe('Estilos', () => {
  function crear() {
    const fixture = TestBed.createComponent(Estilos);
    fixture.detectChanges();
    return fixture;
  }

  function tarjetas(elemento: HTMLElement): HTMLButtonElement[] {
    return Array.from(elemento.querySelectorAll<HTMLButtonElement>('button.estilo'));
  }

  it('muestra los cuatro estilos en orden', () => {
    const elemento = crear().nativeElement as HTMLElement;
    const nombres = tarjetas(elemento).map((b) => b.querySelector('.font-display')?.textContent);
    expect(nombres).toEqual(['Naked', 'Doble propósito', 'Trail', 'Deportiva']);
  });

  it('el conteo de cada estilo suma todas las motos', () => {
    const elemento = crear().nativeElement as HTMLElement;
    const total = tarjetas(elemento)
      .map((b) => parseInt(b.querySelector('.conteo')?.textContent ?? '0', 10))
      .reduce((a, b) => a + b, 0);
    expect(total).toBe(MOTOS.length);
  });

  it('al elegir un estilo filtra el catálogo', () => {
    const fixture = crear();
    tarjetas(fixture.nativeElement)[1].click();
    expect(TestBed.inject(FiltrosService).tipo()).toBe('DOBLE_PROPOSITO');
  });

  it('el conteo cambia con la marca elegida', () => {
    const fixture = crear();
    TestBed.inject(MarcaService).elegir('honda');
    fixture.detectChanges();
    const total = tarjetas(fixture.nativeElement)
      .map((b) => parseInt(b.querySelector('.conteo')?.textContent ?? '0', 10))
      .reduce((a, b) => a + b, 0);
    expect(total).toBe(MOTOS.filter((m) => m.marca === 'honda').length);
  });
});
