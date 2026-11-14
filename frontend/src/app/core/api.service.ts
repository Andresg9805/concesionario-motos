import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export type Parametros = Record<string, string | number | boolean | null | undefined>;

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  url(ruta: string): string {
    const limpia = ruta.startsWith('/') ? ruta : `/${ruta}`;
    return `${this.base}${limpia}`;
  }

  get<T>(ruta: string, parametros?: Parametros): Observable<T> {
    return this.http.get<T>(this.url(ruta), { params: this.armarParametros(parametros) });
  }

  post<T>(ruta: string, cuerpo: unknown): Observable<T> {
    return this.http.post<T>(this.url(ruta), cuerpo);
  }

  put<T>(ruta: string, cuerpo: unknown): Observable<T> {
    return this.http.put<T>(this.url(ruta), cuerpo);
  }

  patch<T>(ruta: string, cuerpo: unknown): Observable<T> {
    return this.http.patch<T>(this.url(ruta), cuerpo);
  }

  delete<T>(ruta: string): Observable<T> {
    return this.http.delete<T>(this.url(ruta));
  }

  private armarParametros(parametros?: Parametros): HttpParams {
    let params = new HttpParams();
    for (const [llave, valor] of Object.entries(parametros ?? {})) {
      if (valor !== null && valor !== undefined && valor !== '') {
        params = params.set(llave, String(valor));
      }
    }
    return params;
  }
}
