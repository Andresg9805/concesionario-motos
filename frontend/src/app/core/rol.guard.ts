import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Rol, SesionService } from './sesion.service';
import { UiService } from './ui.service';

export function soloRol(rol: Rol): CanActivateFn {
  return () => {
    const sesion = inject(SesionService);
    const router = inject(Router);
    if (sesion.rol() === rol) {
      return true;
    }
    if (!sesion.autenticado()) {
      inject(UiService).accesoAbierto.set(true);
    }
    return router.createUrlTree(['/']);
  };
}
