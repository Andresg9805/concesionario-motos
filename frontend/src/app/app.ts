import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Encabezado } from './layout/encabezado/encabezado';
import { Pie } from './layout/pie/pie';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Encabezado, Pie],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {}
