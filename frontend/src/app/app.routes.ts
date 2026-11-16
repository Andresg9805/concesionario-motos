import { Routes } from '@angular/router';
import { soloRol } from './core/rol.guard';
import { Inicio } from './paginas/inicio/inicio';

export const routes: Routes = [
  { path: '', component: Inicio },
  {
    path: 'motos/:id',
    loadComponent: () => import('./paginas/detalle/detalle-moto').then((m) => m.DetalleMoto),
    title: 'Detalle y costo real | Candela Motors',
  },
  {
    path: 'asesor',
    canActivate: [soloRol('ASESOR')],
    loadComponent: () => import('./paginas/asesor/panel-asesor').then((m) => m.PanelAsesor),
    title: 'Panel del asesor | Candela Motors',
  },
  {
    path: 'admin',
    canActivate: [soloRol('ADMIN')],
    loadComponent: () => import('./paginas/admin/panel-admin').then((m) => m.PanelAdmin),
    title: 'Administración | Candela Motors',
  },
  {
    path: 'cuenta',
    canActivate: [soloRol('CLIENTE')],
    loadComponent: () => import('./paginas/cuenta/cuenta').then((m) => m.Cuenta),
    title: 'Mi cuenta | Candela Motors',
  },
  {
    path: 'tienda',
    loadComponent: () => import('./paginas/tienda/tienda').then((m) => m.Tienda),
    title: 'Tienda del motociclista | Candela Motors',
  },
  {
    path: 'carrito',
    loadComponent: () => import('./paginas/tienda/carrito').then((m) => m.Carrito),
    title: 'Carrito | Candela Motors',
  },
  {
    path: 'checkout',
    canActivate: [soloRol('CLIENTE')],
    loadComponent: () => import('./paginas/tienda/checkout').then((m) => m.Checkout),
    title: 'Envío y pago | Candela Motors',
  },
  {
    path: 'pago/resultado',
    canActivate: [soloRol('CLIENTE')],
    loadComponent: () =>
      import('./paginas/tienda/resultado-pago').then((m) => m.ResultadoPagoPagina),
    title: 'Resultado del pago | Candela Motors',
  },
  {
    path: '**',
    loadComponent: () =>
      import('./paginas/no-encontrada/no-encontrada').then((m) => m.NoEncontrada),
    title: 'Página no encontrada | Candela Motors',
  },
];
