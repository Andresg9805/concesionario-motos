import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { App } from './app';
import { routes } from './app.routes';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter(routes), provideHttpClient()],
    }).compileComponents();
  });

  it('se crea la aplicación', () => {
    const fixture = TestBed.createComponent(App);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('muestra el nombre de Candela Motors en el encabezado', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const html = fixture.nativeElement as HTMLElement;
    expect(html.querySelector('.logo-nombre')?.textContent).toContain('Candela Motors');
  });

  it('muestra las tres marcas en el selector', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const html = fixture.nativeElement as HTMLElement;
    const chips = Array.from(html.querySelectorAll('.chip-marca')).map((chip) =>
      chip.textContent?.trim(),
    );
    expect(chips).toEqual(['Honda', 'Kawasaki', 'Yamaha']);
  });
});
