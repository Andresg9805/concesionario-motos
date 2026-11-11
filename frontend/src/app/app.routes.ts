import { Routes } from '@angular/router';
import { Inicio } from './paginas/inicio/inicio';

export const routes: Routes = [
  { path: '', component: Inicio },
  {
    path: '**',
    loadComponent: () =>
      import('./paginas/no-encontrada/no-encontrada').then((m) => m.NoEncontrada),
    title: 'Página no encontrada | Candela Motors',
  },
];
