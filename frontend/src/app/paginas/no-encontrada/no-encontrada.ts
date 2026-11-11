import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-no-encontrada',
  imports: [RouterLink],
  template: `
    <section class="relative overflow-hidden border-b border-line bg-surface2">
      <div
        class="seigaiha pointer-events-none absolute top-0 -right-10 h-40 w-80 opacity-60"
        aria-hidden="true"
      ></div>
      <div class="gutter mx-auto flex max-w-7xl flex-col items-start gap-4 py-20">
        <p class="eyebrow text-muted">Error 404 · 迷子</p>
        <h1 class="font-display text-3xl font-extrabold md:text-[42px]">Esta página no existe.</h1>
        <p class="max-w-xl text-sm text-muted">
          Puede que el enlace esté mal escrito o que la página se haya movido.
        </p>
        <a
          routerLink="/"
          class="cta inline-flex h-10 items-center rounded-md px-4 text-sm font-bold"
          >Volver al inicio</a
        >
      </div>
    </section>
  `,
})
export class NoEncontrada {}
