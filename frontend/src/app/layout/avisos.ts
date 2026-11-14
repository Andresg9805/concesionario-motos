import { Component, inject } from '@angular/core';
import { UiService } from '../core/ui.service';
import { Icono } from '../shared/icono';

@Component({
  selector: 'app-avisos',
  imports: [Icono],
  host: {
    class:
      'pointer-events-none fixed right-4 bottom-4 z-[80] flex w-[min(380px,calc(100vw-32px))] flex-col gap-2',
    role: 'status',
    'aria-live': 'polite',
  },
  template: `
    @for (aviso of ui.avisos(); track aviso.id) {
      <div
        class="pointer-events-auto flex items-start gap-3 rounded-lg border border-line bg-surface px-4 py-3 text-sm shadow-lg"
      >
        <app-icono
          [nombre]="
            aviso.tipo === 'ok'
              ? 'check-circle-2'
              : aviso.tipo === 'error'
                ? 'alert-circle'
                : 'info'
          "
          class="mt-0.5 h-4 w-4"
          [class]="
            aviso.tipo === 'error' ? 'text-danger' : aviso.tipo === 'ok' ? 'text-ok' : 'text-muted'
          "
        />
        <span>{{ aviso.mensaje }}</span>
      </div>
    }
  `,
})
export class Avisos {
  protected readonly ui = inject(UiService);
}
