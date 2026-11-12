import { Component } from '@angular/core';
import { Accesorios } from './secciones/accesorios';
import { Catalogo } from './secciones/catalogo';
import { Cotizar } from './secciones/cotizar';
import { Marcas } from './secciones/marcas';
import { Portada } from './secciones/portada';

@Component({
  selector: 'app-inicio',
  imports: [Portada, Marcas, Catalogo, Accesorios, Cotizar],
  template: `
    <app-portada />
    <app-marcas />
    <app-catalogo />
    <app-accesorios />
    <app-cotizar />
  `,
})
export class Inicio {}
