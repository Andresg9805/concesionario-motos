import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { MARCAS } from '../../core/marcas';
import { SesionService } from '../../core/sesion.service';

interface DatosPanel {
  titulo: string;
  historias: string[];
}

@Component({
  selector: 'app-panel-provisional',
  template: `
    <section class="relative overflow-hidden border-b border-line bg-surface2">
      <div class="resplandor pointer-events-none absolute inset-0" aria-hidden="true"></div>
      <div
        class="seigaiha pointer-events-none absolute top-0 -right-10 h-40 w-80 opacity-60"
        aria-hidden="true"
      ></div>
      <div class="gutter relative mx-auto max-w-7xl py-12">
        <p class="eyebrow eyebrow-marca text-muted">{{ subtitulo() }}</p>
        <h1 class="mt-2 font-display text-3xl font-extrabold md:text-[42px]">
          {{ datos().titulo }}
        </h1>
        <p class="mt-2 max-w-xl text-sm text-muted">
          Hola, {{ sesion.usuario()?.nombre }}. Esta sección se construye en el Sprint 2.
        </p>
        <ul class="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          @for (historia of datos().historias; track historia) {
            <li class="rounded-lg border border-line bg-surface p-4 text-sm">{{ historia }}</li>
          }
        </ul>
      </div>
    </section>
  `,
})
export class PanelProvisional {
  protected readonly sesion = inject(SesionService);
  protected readonly datos = signal(inject(ActivatedRoute).snapshot.data as DatosPanel);
  protected readonly subtitulo = computed(() => {
    const usuario = this.sesion.usuario();
    if (usuario?.rol === 'ASESOR' && usuario.marca) {
      return `Asesor · ${MARCAS[usuario.marca].nombre}`;
    }
    return usuario?.rol === 'ADMIN' ? 'Administración' : '';
  });
}
