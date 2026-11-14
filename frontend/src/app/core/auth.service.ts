import { HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, catchError, map, throwError } from 'rxjs';
import { ApiService } from './api.service';
import { SesionService, Usuario } from './sesion.service';

export interface DatosRegistro {
  nombre: string;
  correo: string;
  celular: string;
  contrasena: string;
}

interface RespuestaToken {
  access_token: string;
  token_type: string;
}

export function mensajeDeError(error: unknown, accion: 'ingresar' | 'registrar'): string {
  const estado = error instanceof HttpErrorResponse ? error.status : -1;
  if (estado === 0) {
    return 'No pudimos conectar con el servidor. Intenta de nuevo en un momento.';
  }
  if (accion === 'ingresar' && (estado === 400 || estado === 401)) {
    return 'Correo o contraseña incorrectos.';
  }
  if (accion === 'registrar' && estado === 409) {
    return 'Ya existe una cuenta con ese correo.';
  }
  if (estado === 422) {
    return 'Revisa los datos del formulario.';
  }
  if (estado === 429) {
    return 'Hiciste muchos intentos. Espera un momento y vuelve a intentar.';
  }
  return 'Algo salió mal. Intenta de nuevo.';
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly api = inject(ApiService);
  private readonly sesion = inject(SesionService);

  ingresar(correo: string, contrasena: string): Observable<Usuario> {
    return this.api.post<RespuestaToken>('/auth/login', { correo, contrasena }).pipe(
      map((respuesta) => {
        const usuario = this.sesion.guardarToken(respuesta.access_token);
        if (!usuario) {
          throw new Error('token');
        }
        return usuario;
      }),
      catchError((error) => throwError(() => new Error(mensajeDeError(error, 'ingresar')))),
    );
  }

  registrar(datos: DatosRegistro): Observable<void> {
    return this.api.post<unknown>('/auth/registro', datos).pipe(
      map(() => undefined),
      catchError((error) => throwError(() => new Error(mensajeDeError(error, 'registrar')))),
    );
  }
}
