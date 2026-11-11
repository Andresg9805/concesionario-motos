import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-no-encontrada',
  imports: [MatButtonModule, RouterLink],
  templateUrl: './no-encontrada.html',
})
export class NoEncontrada {}
