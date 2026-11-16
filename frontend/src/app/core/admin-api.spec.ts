import {
  PedidoAdminApi,
  demandaSinAtender,
  detalleDelError,
  grupoDelPedido,
  licenciaPorCilindraje,
  siguientePaso,
} from './admin-api';

const PEDIDO: PedidoAdminApi = {
  id: 1,
  cliente_nombre: 'Ana Pérez',
  cliente_correo: 'ana@correo.com',
  estado: 'PAGADO',
  estado_pago: 'APROBADO',
  subtotal_cop: 100_000,
  costo_envio_cop: 12_000,
  total_cop: 112_000,
  creado_en: '2026-11-16T10:00:00-05:00',
  items: [],
  envio: { id: 3, numero_guia: 'CM-GUIA-0001', estado: 'PREPARANDO', eventos: [] },
};

describe('reglas del panel del administrador', () => {
  it('el siguiente paso del envío no se salta ninguno', () => {
    expect(siguientePaso('PREPARANDO')?.estado).toBe('ENVIADO');
    expect(siguientePaso('EN_CAMINO')?.estado).toBe('ENTREGADO');
    expect(siguientePaso('ENTREGADO')).toBeNull();
  });

  it('agrupa los pedidos según el pago y el envío', () => {
    expect(grupoDelPedido(PEDIDO)).toBe('despachar');
    expect(grupoDelPedido({ ...PEDIDO, estado: 'PENDIENTE_PAGO', envio: null })).toBe('pendientes');
    expect(grupoDelPedido({ ...PEDIDO, envio: { ...PEDIDO.envio!, estado: 'ENTREGADO' } })).toBe(
      'entregados',
    );
  });

  it('la licencia sale del cilindraje', () => {
    expect(licenciaPorCilindraje(125)).toBe('A1');
    expect(licenciaPorCilindraje(126)).toBe('A2');
  });

  it('muestra el campo que falló cuando el servidor responde 422', () => {
    const error = {
      error: { detail: [{ loc: ['body', 'precio_cop'], msg: 'debe ser mayor que 0' }] },
    };
    expect(detalleDelError(error, 'x')).toBe('Revisa el campo precio_cop: debe ser mayor que 0');
    expect(detalleDelError({ error: { detail: 'No existe' } }, 'x')).toBe('No existe');
    expect(detalleDelError(null, 'Falló')).toBe('Falló');
  });

  it('marca como demanda sin atender cuando hay búsquedas y casi no hay motos', () => {
    const fila = {
      rango: 'Menos de $300.000',
      licencia: 'A2' as const,
      busquedas: 10,
      sin_resultados: 8,
      promedio_resultados: 0.4,
      motos_en_stock: 1,
    };
    expect(demandaSinAtender(fila)).toBe(true);
    expect(demandaSinAtender({ ...fila, motos_en_stock: 6 })).toBe(false);
  });
});
