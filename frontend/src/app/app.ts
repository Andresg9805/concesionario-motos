import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MarcaService } from './core/marca.service';
import { TemaService } from './core/tema.service';
import { AccesoDialogo } from './dialogos/acceso-dialogo';
import { CotizarDialogo } from './dialogos/cotizar-dialogo';
import { Avisos } from './layout/avisos';
import { Encabezado } from './layout/encabezado';
import { Pie } from './layout/pie';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Encabezado, Pie, Avisos, CotizarDialogo, AccesoDialogo],
  host: { class: 'theme-t flex min-h-screen flex-col' },
  template: `
    <a
      href="#catalogo"
      class="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[70] focus:rounded focus:bg-surface focus:px-3 focus:py-2"
      >Saltar al catálogo</a
    >
    <app-encabezado />
    <main class="flex-1">
      <router-outlet />
    </main>
    <app-pie />
    <app-cotizar-dialogo />
    <app-acceso-dialogo />
    <app-avisos />
  `,
})
export class App {
  constructor() {
    inject(MarcaService);
    inject(TemaService);
  }
}
