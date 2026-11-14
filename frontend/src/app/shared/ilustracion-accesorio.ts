import { Component, input } from '@angular/core';
import { IlustracionAccesorio as Tipo } from '../core/modelos';

@Component({
  selector: 'app-ilustracion-accesorio',
  host: { class: 'block h-full w-full' },
  template: `
    <svg viewBox="0 0 160 120" class="h-full w-full" aria-hidden="true">
      @switch (tipo()) {
        @case ('casco') {
          <path
            d="M28 84 Q26 30 80 26 Q132 26 134 74 L134 94 L62 94 Q36 94 28 84 Z"
            fill="currentColor"
          />
          <path
            d="M80 50 Q112 44 132 58 L132 76 L88 76 Q76 66 80 50 Z"
            fill="var(--surface-2)"
            opacity=".85"
          />
          <path d="M40 70 L70 68" stroke="var(--surface-2)" stroke-width="3" opacity=".5" />
        }
        @case ('chaqueta') {
          <path
            d="M56 22 L80 30 L104 22 L132 36 L142 96 L124 98 L118 58 L116 104 L44 104 L42 58 L36 98 L18 96 L28 36 Z"
            fill="currentColor"
          />
          <path d="M80 30 L80 104" stroke="var(--surface-2)" stroke-width="2.5" opacity=".6" />
          <rect x="30" y="40" width="14" height="22" rx="5" fill="var(--surface-2)" opacity=".45" />
          <rect
            x="116"
            y="40"
            width="14"
            height="22"
            rx="5"
            fill="var(--surface-2)"
            opacity=".45"
          />
        }
        @case ('guantes') {
          <path
            d="M44 104 L44 60 Q44 50 52 50 L52 30 Q52 22 59 22 Q66 22 66 30 L66 48 L68 24 Q68 16 75 16 Q82 16 82 24 L82 48 L84 28 Q84 20 91 20 Q98 20 98 28 L98 52 L100 38 Q100 31 106 31 Q112 31 112 38 L112 76 Q112 92 100 104 Z"
            fill="currentColor"
          />
          <path
            d="M54 56 L106 56"
            stroke="var(--surface-2)"
            stroke-width="6"
            stroke-linecap="round"
            opacity=".55"
          />
          <rect x="44" y="88" width="62" height="12" rx="4" fill="var(--surface-2)" opacity=".4" />
        }
        @case ('rodillera') {
          <path d="M60 18 Q80 10 100 18 L104 100 Q80 110 56 100 Z" fill="currentColor" />
          <ellipse cx="80" cy="50" rx="18" ry="22" fill="var(--surface-2)" opacity=".5" />
          <path
            d="M50 36 L110 36 M48 82 L112 82"
            stroke="currentColor"
            stroke-width="7"
            stroke-linecap="round"
          />
        }
        @case ('hombrera') {
          <path d="M26 64 Q30 30 60 28 Q72 30 74 46 L70 74 Q46 82 26 64 Z" fill="currentColor" />
          <path
            d="M134 64 Q130 30 100 28 Q88 30 86 46 L90 74 Q114 82 134 64 Z"
            fill="currentColor"
          />
          <rect x="66" y="38" width="28" height="70" rx="10" fill="currentColor" opacity=".75" />
          <path
            d="M70 56 L90 56 M70 72 L90 72 M70 88 L90 88"
            stroke="var(--surface-2)"
            stroke-width="2.5"
            opacity=".6"
          />
        }
        @case ('maleta') {
          <rect x="30" y="34" width="100" height="66" rx="16" fill="currentColor" />
          <path d="M30 60 L130 60" stroke="var(--surface-2)" stroke-width="3" opacity=".6" />
          <rect x="66" y="22" width="28" height="12" rx="4" fill="currentColor" opacity=".75" />
          <rect x="72" y="66" width="16" height="10" rx="3" fill="var(--surface-2)" opacity=".6" />
          <rect x="40" y="84" width="22" height="6" rx="3" fill="var(--surface-2)" opacity=".5" />
          <rect x="98" y="84" width="22" height="6" rx="3" fill="var(--surface-2)" opacity=".5" />
        }
        @case ('mantenimiento') {
          <rect x="34" y="40" width="34" height="64" rx="8" fill="currentColor" />
          <rect x="42" y="26" width="18" height="14" rx="3" fill="currentColor" opacity=".75" />
          <rect x="40" y="58" width="22" height="24" rx="3" fill="var(--surface-2)" opacity=".5" />
          <path
            d="M88 100 L118 46"
            stroke="currentColor"
            stroke-width="10"
            stroke-linecap="round"
          />
          <circle cx="122" cy="38" r="15" fill="currentColor" />
          <circle cx="122" cy="38" r="7" fill="var(--surface-2)" />
        }
      }
    </svg>
  `,
})
export class IlustracionAccesorio {
  readonly tipo = input.required<Tipo>();
}
