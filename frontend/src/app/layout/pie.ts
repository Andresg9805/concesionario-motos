import { Component } from '@angular/core';

@Component({
  selector: 'app-pie',
  host: { class: 'relative block border-t border-line bg-surface' },
  template: `
    <div class="linea-marca absolute inset-x-0 -top-px" aria-hidden="true"></div>
    <div
      class="gutter mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 py-6 text-xs text-muted"
    >
      <span>Candela Motors · Calidad japonesa · Bogotá, Colombia</span>
      <span>Las motos se cotizan con un asesor. Los accesorios se compran en línea.</span>
    </div>
  `,
})
export class Pie {}
