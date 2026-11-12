import { TestBed } from '@angular/core/testing';
import { ALFABETO_CODIGO, AtencionService, FORMATO_CODIGO } from './atencion.service';
import { MOTOS } from './datos-prueba';

describe('AtencionService', () => {
  let atencion: AtencionService;

  beforeEach(() => {
    atencion = TestBed.inject(AtencionService);
  });

  it('el alfabeto del código no tiene O, 0, I ni 1', () => {
    expect(ALFABETO_CODIGO).not.toMatch(/[O0I1]/);
  });

  it('genera códigos con formato CM-XXXX', () => {
    for (let i = 0; i < 20; i++) {
      expect(atencion.generarCodigo()).toMatch(FORMATO_CODIGO);
    }
  });

  it('elige el asesor de la marca con menos atenciones abiertas', () => {
    expect(atencion.elegirAsesor('kawasaki').nombre).toBe('Santiago Mejía');
  });

  it('una cotización empieza en NUEVO y un test drive en PENDIENTE', () => {
    const moto = MOTOS.find((m) => m.id === 'y-mt03')!;
    expect(atencion.registrar(moto, 'cotizacion').estado).toBe('NUEVO');
    expect(atencion.registrar(moto, 'testdrive').estado).toBe('PENDIENTE');
  });

  it('se puede consultar lo que se registró y el código de ejemplo', () => {
    const moto = MOTOS[0];
    const nueva = atencion.registrar(moto, 'cotizacion');
    expect(atencion.consultar(nueva.codigo.toLowerCase())?.moto).toBe(moto.modelo);
    expect(atencion.consultar('CM-7K2Q')?.estado).toBe('CONTACTADO');
    expect(atencion.consultar('CM-ZZZZ')).toBeUndefined();
  });
});
