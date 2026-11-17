import { TestBed } from '@angular/core/testing';
import { CarritoService, llaveDelCarrito } from './carrito.service';
import { ACCESORIOS } from './datos-prueba';
import { SesionService } from './sesion.service';

function token(id: string): string {
  const parte = (datos: object) => btoa(JSON.stringify(datos)).replace(/=+$/, '');
  const exp = Math.floor(Date.now() / 1000) + 3600;
  return `${parte({ alg: 'HS256' })}.${parte({ sub: id, nombre: 'Cliente ' + id, rol: 'CLIENTE', exp })}.firma`;
}

describe('CarritoService', () => {
  let carrito: CarritoService;
  const conStock = ACCESORIOS.find((a) => a.stock >= 3)!;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({});
    carrito = TestBed.inject(CarritoService);
  });

  it('agrega accesorios y suma el subtotal', () => {
    carrito.agregar(conStock);
    carrito.agregar(conStock);
    expect(carrito.unidades()).toBe(2);
    expect(carrito.subtotal()).toBe(conStock.precio * 2);
  });

  it('no deja pasar del stock disponible', () => {
    carrito.fijar(conStock, conStock.stock);
    expect(carrito.agregar(conStock)).toBe(false);
    expect(carrito.cantidadDe(conStock.id)).toBe(conStock.stock);
    carrito.fijar(conStock, conStock.stock + 10);
    expect(carrito.cantidadDe(conStock.id)).toBe(conStock.stock);
  });

  it('con cantidad cero quita el accesorio', () => {
    carrito.agregar(conStock);
    carrito.fijar(conStock, 0);
    expect(carrito.vacio()).toBe(true);
  });

  it('guarda el carrito en el navegador', () => {
    carrito.agregar(conStock);
    TestBed.flushEffects();
    expect(JSON.parse(localStorage.getItem('cm-carrito') ?? '[]')).toEqual([
      { accesorioId: conStock.id, cantidad: 1 },
    ]);
  });

  it('cada cuenta tiene su propio carrito', () => {
    const sesion = TestBed.inject(SesionService);
    sesion.guardarToken(token('1'));
    TestBed.flushEffects();
    carrito.agregar(conStock);
    expect(carrito.unidades()).toBe(1);

    sesion.guardarToken(token('2'));
    TestBed.flushEffects();
    expect(carrito.vacio()).toBe(true);

    sesion.guardarToken(token('1'));
    TestBed.flushEffects();
    expect(carrito.unidades()).toBe(1);
  });

  it('al cerrar sesión el carrito de la cuenta no queda a la vista', () => {
    const sesion = TestBed.inject(SesionService);
    sesion.guardarToken(token('1'));
    TestBed.flushEffects();
    carrito.agregar(conStock);

    sesion.cerrarSesion();
    TestBed.flushEffects();

    expect(carrito.vacio()).toBe(true);
    expect(localStorage.getItem(llaveDelCarrito('1'))).not.toBeNull();
  });

  it('lo que el visitante agregó pasa a su cuenta al iniciar sesión', () => {
    carrito.agregar(conStock);
    const sesion = TestBed.inject(SesionService);

    sesion.guardarToken(token('3'));
    TestBed.flushEffects();

    expect(carrito.unidades()).toBe(1);
    expect(localStorage.getItem('cm-carrito')).toBeNull();
    sesion.cerrarSesion();
    TestBed.flushEffects();
    expect(carrito.vacio()).toBe(true);
  });
});
