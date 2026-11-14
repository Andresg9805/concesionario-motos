import { TestBed } from '@angular/core/testing';
import { CarritoService } from './carrito.service';
import { ACCESORIOS } from './datos-prueba';

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
});
