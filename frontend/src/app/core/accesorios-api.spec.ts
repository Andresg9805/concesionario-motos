import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { accesorioDesdeApi } from './accesorios-api';
import { CatalogoService } from './catalogo.service';
import { ACCESORIOS } from './datos-prueba';

const CASCO = {
  id: 1,
  sku: 'CAS-001',
  nombre: 'X-Fifteen',
  categoria: 'CASCO',
  fabricante: 'SHOEI',
  descripcion: 'Doble visor.',
  precio_cop: 489000,
  stock: 12,
  imagen_url: '',
};

describe('Accesorios desde la API', () => {
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('convierte la categoría y usa el id del servidor', () => {
    expect(accesorioDesdeApi(CASCO)).toEqual({
      id: '1',
      categoria: 'Cascos',
      nombre: 'X-Fifteen',
      fabricante: 'SHOEI',
      descripcion: 'Doble visor.',
      precio: 489000,
      stock: 12,
      ilustracion: 'casco',
    });
  });

  it('usa la imagen que viene de la base de datos', () => {
    const conFoto = accesorioDesdeApi({ ...CASCO, imagen_url: '/accesorios/cas-001.webp' });
    expect(conFoto.imagen).toBe('/accesorios/cas-001.webp');
    expect(accesorioDesdeApi(CASCO).imagen).toBeUndefined();
  });

  it('si no llega el fabricante no se muestra', () => {
    expect(accesorioDesdeApi({ ...CASCO, fabricante: '' }).fabricante).toBeUndefined();
  });

  it('una categoría nueva se muestra con su nombre', () => {
    expect(accesorioDesdeApi({ ...CASCO, categoria: 'BOTAS' }).categoria).toBe('Botas');
  });

  it('la tienda usa los accesorios de la API y si falla se queda con los de prueba', () => {
    const catalogo = TestBed.inject(CatalogoService);
    catalogo.cargarAccesorios();
    http.expectOne('http://localhost:8000/accesorios').flush([CASCO]);
    expect(catalogo.accesorios()).toHaveLength(1);

    const otro = TestBed.inject(CatalogoService);
    otro.origenAccesorios.set('prueba');
    otro.accesorios.set(ACCESORIOS);
    otro.cargarAccesorios();
    http
      .expectOne('http://localhost:8000/accesorios')
      .flush('', { status: 0, statusText: 'Unknown Error' });
    expect(otro.accesorios()).toHaveLength(ACCESORIOS.length);
  });
});
