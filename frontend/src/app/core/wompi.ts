import { Injectable } from '@angular/core';
import { DatosWompi } from './tienda-api';

interface Transaccion {
  id: string;
  status: string;
}

interface WidgetCheckout {
  open(callback: (resultado: { transaction?: Transaccion }) => void): void;
}

type ConstructorWidget = new (opciones: Record<string, unknown>) => WidgetCheckout;

const SCRIPT_WOMPI = 'https://checkout.wompi.co/widget.js';

@Injectable({ providedIn: 'root' })
export class WompiService {
  private carga: Promise<ConstructorWidget> | null = null;

  abrir(datos: DatosWompi, urlRetorno: string): Promise<Transaccion | null> {
    return this.cargar().then(
      (Widget) =>
        new Promise((resolver) => {
          const widget = new Widget({
            currency: datos.moneda,
            amountInCents: datos.monto_centavos,
            reference: datos.referencia,
            publicKey: datos.llave_publica,
            signature: { integrity: datos.firma_integridad },
            redirectUrl: urlRetorno,
          });
          widget.open((resultado) => resolver(resultado.transaction ?? null));
        }),
    );
  }

  private cargar(): Promise<ConstructorWidget> {
    const existente = (window as unknown as { WidgetCheckout?: ConstructorWidget }).WidgetCheckout;
    if (existente) {
      return Promise.resolve(existente);
    }
    this.carga ??= new Promise((resolver, rechazar) => {
      const script = document.createElement('script');
      script.src = SCRIPT_WOMPI;
      script.async = true;
      script.onload = () => {
        const widget = (window as unknown as { WidgetCheckout?: ConstructorWidget }).WidgetCheckout;
        if (widget) {
          resolver(widget);
        } else {
          rechazar(new Error('Wompi no cargó'));
        }
      };
      script.onerror = () => {
        this.carga = null;
        rechazar(new Error('Wompi no cargó'));
      };
      document.head.appendChild(script);
    });
    return this.carga;
  }
}
