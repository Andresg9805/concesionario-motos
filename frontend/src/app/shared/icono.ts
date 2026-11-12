import { Component, computed, input } from '@angular/core';
import {
  ArrowDown,
  Check,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  CircleAlert,
  Copy,
  Eye,
  EyeOff,
  FileText,
  Flag,
  Headset,
  IdCard,
  IconNode,
  Info,
  LogIn,
  LogOut,
  Menu,
  Moon,
  Pause,
  Play,
  ScanSearch,
  Search,
  Send,
  Shield,
  ShoppingBag,
  Sun,
  User,
  UserPlus,
  Wallet,
  X,
} from 'lucide';

const ICONOS: Record<string, IconNode> = {
  'arrow-down': ArrowDown,
  check: Check,
  'check-circle-2': CheckCircle2,
  'chevron-left': ChevronLeft,
  'chevron-right': ChevronRight,
  'alert-circle': CircleAlert,
  copy: Copy,
  eye: Eye,
  'eye-off': EyeOff,
  'file-text': FileText,
  flag: Flag,
  headset: Headset,
  'id-card': IdCard,
  info: Info,
  'log-in': LogIn,
  'log-out': LogOut,
  menu: Menu,
  moon: Moon,
  pause: Pause,
  play: Play,
  'scan-search': ScanSearch,
  search: Search,
  send: Send,
  shield: Shield,
  'shopping-bag': ShoppingBag,
  sun: Sun,
  user: User,
  'user-plus': UserPlus,
  wallet: Wallet,
  x: X,
};

@Component({
  selector: 'app-icono',
  host: { class: 'inline-block shrink-0', 'aria-hidden': 'true' },
  template: `
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="block h-full w-full"
    >
      @for (parte of partes(); track $index) {
        @switch (parte[0]) {
          @case ('path') {
            <svg:path [attr.d]="parte[1]['d']" />
          }
          @case ('circle') {
            <svg:circle
              [attr.cx]="parte[1]['cx']"
              [attr.cy]="parte[1]['cy']"
              [attr.r]="parte[1]['r']"
            />
          }
          @case ('rect') {
            <svg:rect
              [attr.x]="parte[1]['x']"
              [attr.y]="parte[1]['y']"
              [attr.width]="parte[1]['width']"
              [attr.height]="parte[1]['height']"
              [attr.rx]="parte[1]['rx']"
              [attr.ry]="parte[1]['ry']"
            />
          }
          @case ('line') {
            <svg:line
              [attr.x1]="parte[1]['x1']"
              [attr.y1]="parte[1]['y1']"
              [attr.x2]="parte[1]['x2']"
              [attr.y2]="parte[1]['y2']"
            />
          }
          @case ('polyline') {
            <svg:polyline [attr.points]="parte[1]['points']" />
          }
          @case ('polygon') {
            <svg:polygon [attr.points]="parte[1]['points']" />
          }
          @case ('ellipse') {
            <svg:ellipse
              [attr.cx]="parte[1]['cx']"
              [attr.cy]="parte[1]['cy']"
              [attr.rx]="parte[1]['rx']"
              [attr.ry]="parte[1]['ry']"
            />
          }
        }
      }
    </svg>
  `,
})
export class Icono {
  readonly nombre = input.required<string>();

  protected readonly partes = computed(
    () => (ICONOS[this.nombre()] ?? []) as unknown as [string, Record<string, string | number>][],
  );
}
