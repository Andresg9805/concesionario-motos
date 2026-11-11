import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-moto-detalle',
  imports: [RouterLink],
  templateUrl: './moto-detalle.html',
})
export class MotoDetalle {
  readonly id = input.required<string>();
}
