import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';
import { MarcaService } from '../../core/marca.service';
import { MARCAS } from '../../core/marcas';

@Component({
  selector: 'app-inicio',
  imports: [MatButtonModule, RouterLink],
  templateUrl: './inicio.html',
  styleUrl: './inicio.scss',
})
export class Inicio {
  protected readonly marcaService = inject(MarcaService);
  protected readonly marcas = MARCAS;
}
