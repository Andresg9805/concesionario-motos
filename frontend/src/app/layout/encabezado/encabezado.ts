import { Component, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { MarcaService } from '../../core/marca.service';
import { MARCAS } from '../../core/marcas';
import { SesionService } from '../../core/sesion.service';

@Component({
  selector: 'app-encabezado',
  imports: [MatToolbarModule, MatButtonModule, MatIconModule, RouterLink, RouterLinkActive],
  templateUrl: './encabezado.html',
  styleUrl: './encabezado.scss',
})
export class Encabezado {
  protected readonly marcaService = inject(MarcaService);
  protected readonly sesion = inject(SesionService);
  protected readonly marcas = MARCAS;
  protected readonly menuAbierto = signal(false);

  protected readonly enlaces = [
    { ruta: '/', texto: 'Inicio', exacto: true },
    { ruta: '/motos', texto: 'Motos', exacto: false },
    { ruta: '/accesorios', texto: 'Accesorios', exacto: false },
    { ruta: '/seguimiento', texto: 'Seguimiento', exacto: false },
  ];

  protected alternarMenu(): void {
    this.menuAbierto.update((abierto) => !abierto);
  }

  protected cerrarMenu(): void {
    this.menuAbierto.set(false);
  }
}
