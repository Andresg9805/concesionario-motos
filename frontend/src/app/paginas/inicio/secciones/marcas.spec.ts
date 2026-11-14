import { TestBed } from '@angular/core/testing';
import { FiltrosService } from '../../../core/filtros.service';
import { Marcas } from './marcas';

describe('Marcas', () => {
  function botonesTipo(elemento: HTMLElement): HTMLButtonElement[] {
    return Array.from(elemento.querySelectorAll<HTMLButtonElement>('button.tipo'));
  }

  it('cada recuadro de tipo filtra el catálogo y al volver a tocarlo se quita', () => {
    const fixture = TestBed.createComponent(Marcas);
    fixture.detectChanges();
    const filtros = TestBed.inject(FiltrosService);
    const botones = botonesTipo(fixture.nativeElement);
    expect(botones).toHaveLength(4);
    botones[3].click();
    expect(filtros.tipo()).toBe('DEPORTIVA');
    fixture.detectChanges();
    expect(botones[3].getAttribute('aria-pressed')).toBe('true');
    botones[3].click();
    expect(filtros.tipo()).toBe('todos');
  });
});
