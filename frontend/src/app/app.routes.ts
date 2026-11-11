import { Routes } from '@angular/router';
import { Inicio } from './paginas/inicio/inicio';

export const routes: Routes = [
  { path: '', component: Inicio, title: 'Candela Motors' },
  {
    path: 'motos',
    loadComponent: () => import('./paginas/motos/motos').then((m) => m.Motos),
    title: 'Motos | Candela Motors',
  },
  {
    path: 'motos/:id',
    loadComponent: () => import('./paginas/moto-detalle/moto-detalle').then((m) => m.MotoDetalle),
    title: 'Detalle | Candela Motors',
  },
  {
    path: 'accesorios',
    loadComponent: () => import('./paginas/accesorios/accesorios').then((m) => m.Accesorios),
    title: 'Accesorios | Candela Motors',
  },
  {
    path: 'seguimiento',
    loadComponent: () => import('./paginas/seguimiento/seguimiento').then((m) => m.Seguimiento),
    title: 'Seguimiento | Candela Motors',
  },
  {
    path: 'ingresar',
    loadComponent: () => import('./paginas/ingresar/ingresar').then((m) => m.Ingresar),
    title: 'Ingresar | Candela Motors',
  },
  {
    path: '**',
    loadComponent: () =>
      import('./paginas/no-encontrada/no-encontrada').then((m) => m.NoEncontrada),
    title: 'No encontrada | Candela Motors',
  },
];
