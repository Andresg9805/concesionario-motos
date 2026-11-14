import { Pipe, PipeTransform } from '@angular/core';
import { formatoCop } from '../core/finanzas';

@Pipe({ name: 'cop' })
export class CopPipe implements PipeTransform {
  transform(valor: number | null | undefined): string {
    return valor == null ? '' : formatoCop(valor);
  }
}
