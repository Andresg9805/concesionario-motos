import { Component, input } from '@angular/core';
import { Silueta } from '../core/modelos';

@Component({
  selector: 'app-silueta-moto',
  host: { class: 'block h-full w-full' },
  template: `
    <svg viewBox="0 0 240 140" class="h-full w-full" aria-hidden="true">
      @switch (tipo()) {
        @case ('sport') {
          <circle cx="52" cy="106" r="26" fill="none" stroke="currentColor" stroke-width="7" />
          <circle cx="52" cy="106" r="5" fill="currentColor" />
          <circle cx="188" cy="106" r="26" fill="none" stroke="currentColor" stroke-width="7" />
          <circle cx="188" cy="106" r="5" fill="currentColor" />
          <path
            d="M52 106 L118 92 M188 106 L176 62"
            stroke="currentColor"
            stroke-width="6"
            stroke-linecap="round"
            fill="none"
          />
          <path
            d="M62 96 L88 72 L122 66 L150 50 L178 44 L206 62 L202 82 L168 86 L140 96 Z"
            fill="currentColor"
          />
          <path d="M38 64 L98 60 L94 70 L50 74 Z" fill="currentColor" />
          <path d="M152 58 L184 50 L196 62 L162 68 Z" class="acc" />
        }
        @case ('trail') {
          <circle cx="50" cy="102" r="29" fill="none" stroke="currentColor" stroke-width="7" />
          <circle cx="50" cy="102" r="5" fill="currentColor" />
          <circle cx="192" cy="102" r="29" fill="none" stroke="currentColor" stroke-width="7" />
          <circle cx="192" cy="102" r="5" fill="currentColor" />
          <path
            d="M50 102 L106 82 M192 102 L168 38 M158 34 L180 36"
            stroke="currentColor"
            stroke-width="6"
            stroke-linecap="round"
            fill="none"
          />
          <path d="M46 54 L108 52 L106 60 L54 64 Z" fill="currentColor" />
          <path d="M104 52 Q124 40 148 46 L152 60 L106 66 Z" fill="currentColor" />
          <rect x="108" y="66" width="40" height="24" rx="4" fill="currentColor" />
          <path d="M168 64 L206 58 L208 65 L172 71 Z" fill="currentColor" />
          <path d="M60 64 L98 62 L94 76 L66 78 Z" class="acc" />
        }
        @case ('doble') {
          <circle cx="50" cy="104" r="27" fill="none" stroke="currentColor" stroke-width="7" />
          <circle cx="50" cy="104" r="5" fill="currentColor" />
          <circle cx="192" cy="102" r="29" fill="none" stroke="currentColor" stroke-width="7" />
          <circle cx="192" cy="102" r="5" fill="currentColor" />
          <path
            d="M50 104 L108 84 M192 102 L170 44 M160 38 L182 40"
            stroke="currentColor"
            stroke-width="6"
            stroke-linecap="round"
            fill="none"
          />
          <path d="M24 56 L60 54 L62 66 L30 68 Z" fill="currentColor" />
          <rect x="32" y="40" width="26" height="14" rx="3" fill="currentColor" opacity=".75" />
          <path d="M58 56 L108 54 L108 64 L62 68 Z" fill="currentColor" />
          <path d="M106 50 Q128 38 156 44 L160 62 L108 68 Z" fill="currentColor" />
          <rect x="110" y="68" width="42" height="24" rx="4" fill="currentColor" />
          <path d="M166 58 L196 40 L204 46 L178 66 Z" fill="currentColor" />
          <path d="M190 42 L198 24 L208 28 L202 44 Z" fill="currentColor" opacity=".55" />
          <path d="M70 58 L100 57 L98 66 L74 68 Z" class="acc" />
        }
        @default {
          <circle cx="52" cy="106" r="26" fill="none" stroke="currentColor" stroke-width="7" />
          <circle cx="52" cy="106" r="5" fill="currentColor" />
          <circle cx="188" cy="106" r="26" fill="none" stroke="currentColor" stroke-width="7" />
          <circle cx="188" cy="106" r="5" fill="currentColor" />
          <path
            d="M52 106 L104 86 M188 106 L170 50 M160 42 L180 44"
            stroke="currentColor"
            stroke-width="6"
            stroke-linecap="round"
            fill="none"
          />
          <path d="M98 62 Q118 44 150 50 L158 66 L104 74 Z" fill="currentColor" />
          <path d="M56 62 L100 60 L102 70 L60 72 Z" fill="currentColor" />
          <rect x="104" y="74" width="48" height="24" rx="4" fill="currentColor" />
          <circle cx="176" cy="58" r="8" fill="currentColor" />
          <path d="M110 58 Q128 48 146 52 L150 58 L114 64 Z" class="acc" />
        }
      }
    </svg>
  `,
})
export class SiluetaMoto {
  readonly tipo = input<Silueta>('naked');
}
