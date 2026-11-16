import { EventoEnvioApi, fechaDelPaso, pasoActual } from './cuenta-api';

describe('reglas de la cuenta del cliente', () => {
  it('el paso actual del envío sigue el orden preparando, enviado, en camino y entregado', () => {
    expect(pasoActual(null)).toBe(-1);
    expect(pasoActual('PREPARANDO')).toBe(0);
    expect(pasoActual('EN_CAMINO')).toBe(2);
    expect(pasoActual('ENTREGADO')).toBe(3);
  });

  it('busca la fecha en que el envío llegó a cada paso', () => {
    const eventos: EventoEnvioApi[] = [
      { estado: 'PREPARANDO', fecha: '2026-11-16T10:00:00-05:00', nota: 'Pago aprobado' },
      { estado: 'ENVIADO', fecha: '2026-11-16T15:00:00-05:00', nota: '' },
    ];
    expect(fechaDelPaso(eventos, 'ENVIADO')).toBe('2026-11-16T15:00:00-05:00');
    expect(fechaDelPaso(eventos, 'ENTREGADO')).toBeNull();
  });
});
