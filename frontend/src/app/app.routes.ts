import { Routes } from '@angular/router';
import { soloRol } from './core/rol.guard';
import { Inicio } from './paginas/inicio/inicio';

export const routes: Routes = [
  { path: '', component: Inicio },
  {
    path: 'asesor',
    canActivate: [soloRol('ASESOR')],
    loadComponent: () =>
      import('./paginas/panel/panel-provisional').then((m) => m.PanelProvisional),
    title: 'Panel del asesor | Candela Motors',
    data: {
      titulo: 'Panel del asesor',
      historias: ['Mis atenciones y sus estados (HU-06)', 'Cola de test drives (HU-06)'],
    },
  },
  {
    path: 'admin',
    canActivate: [soloRol('ADMIN')],
    loadComponent: () =>
      import('./paginas/panel/panel-provisional').then((m) => m.PanelProvisional),
    title: 'Administración | Candela Motors',
    data: {
      titulo: 'Administración',
      historias: [
        'Gestión de envíos (HU-11)',
        'Motos, accesorios y parámetros de costo (HU-12)',
        'Radar de demanda (HU-13)',
      ],
    },
  },
  {
    path: '**',
    loadComponent: () =>
      import('./paginas/no-encontrada/no-encontrada').then((m) => m.NoEncontrada),
    title: 'Página no encontrada | Candela Motors',
  },
];
