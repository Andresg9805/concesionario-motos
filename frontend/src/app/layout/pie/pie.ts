import { Component } from '@angular/core';

@Component({
  selector: 'app-pie',
  templateUrl: './pie.html',
  styleUrl: './pie.scss',
})
export class Pie {
  protected readonly anio = new Date().getFullYear();
}
