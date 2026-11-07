# Alcance final del proyecto: Candela Motors

Este documento es la fuente oficial de lo que vamos a construir. Se acordó en el grupo el 6 de noviembre de 2026. Si algo cambia, se cambia aquí con un Pull Request.

## 1. La idea

**Candela Motors** es un concesionario que solo vende motos japonesas de tres marcas:

| Marca | Color en la página |
| --- | --- |
| Honda | Rojo |
| Kawasaki | Verde |
| Yamaha | Azul |

**Consigna:** *Calidad japonesa.*

La mayoría de páginas de concesionarios son un folleto: fotos, precio y un botón de "contáctenos". Candela Motors quiere ser útil de verdad:

1. Ayuda a decidir qué moto comprar con números reales: cuánto cuesta tenerla cada mes, no solo el precio.
2. Le asigna a cada cliente un asesor especialista en la marca que le interesa, sin obligarlo a crear una cuenta.
3. Vende accesorios en línea con pago virtual y seguimiento del envío.

Las motos no se venden en línea (casi nadie compra una moto por internet). Los accesorios sí.

## 2. Actores

| Actor | Necesita cuenta | Qué hace |
| --- | --- | --- |
| Visitante | No | Ve el catálogo, busca por cuota, calcula el costo real, cotiza, pide test drive y consulta su seguimiento con un código |
| Cliente | Sí (rol `CLIENTE`) | Todo lo del visitante, además compra accesorios, guarda direcciones y ve sus pedidos y cotizaciones |
| Asesor | Sí (rol `ASESOR`) | Atiende a los clientes de su marca: cambia el estado de cada atención y maneja su cola de test drives |
| Administrador | Sí (rol `ADMIN`) | Maneja motos, accesorios, parámetros de costo y envíos, y ve los reportes |
| Wompi | Sistema externo | Procesa el pago y avisa el resultado (ambiente de pruebas) |
| datos.gov.co | Sistema externo | Entrega la TRM y el listado de departamentos y municipios (DIVIPOLA) |

## 3. Módulos

### 3.1 Motos y costo real

- Catálogo de motos Honda, Kawasaki y Yamaha, cada marca con su color. Filtros por marca, tipo, licencia y precio.
- **Buscar por cuota:** el visitante dice cuánto puede pagar al mes, cuánto tiene de cuota inicial y qué licencia tiene (A1 o A2). La página le muestra las motos que puede pagar. Se usa la fórmula del crédito al revés para hallar el precio máximo, y el árbol binario de motos busca ese rango de precios.
- **Costo real mensual:** cuota del crédito + gasolina + SOAT + mantenimiento + impuesto, según cuántos kilómetros anda al mes y para qué usa la moto (ciudad, carretera o trabajo).
- **Modo trabajo:** para domiciliarios y mensajeros, muestra en cuántos meses se paga la moto con lo que gana.
- Simulador de crédito con opción de deshacer (pila).
- Precio de referencia en dólares con la TRM del día (dato informativo).
- Cada búsqueda queda guardada sin datos personales, para el radar de demanda.

### 3.2 Atención personalizada

- El visitante cotiza una moto o pide un test drive dejando su nombre, correo y celular. No necesita cuenta.
- El sistema le asigna automáticamente un **asesor especialista en la marca** de la moto y le muestra su nombre y un enlace de WhatsApp.
- El visitante recibe un **código de seguimiento** (por ejemplo `CM-7F3K`) para consultar cómo va su atención.
- El asesor entra a su panel y ve sus clientes. Cada atención avanza por estos estados:
  `NUEVO → CONTACTADO → TEST_DRIVE → NEGOCIANDO → VENDIDO` o `DESCARTADO`.
- Cada asesor tiene su **cola de test drives** (FIFO) y atiende al siguiente.
- Si el cliente tiene cuenta, sus cotizaciones también aparecen en "Mi cuenta".

### 3.3 Tienda de accesorios

- Catálogo de accesorios por categoría (cascos, chaquetas, guantes, maletas, mantenimiento) y por moto compatible: "accesorios para tu MT-03".
- Registro e inicio de sesión del cliente.
- Carrito y direcciones de envío guardadas. Los departamentos y municipios son los oficiales del DANE.
- **Pago 100 % virtual con Wompi** en ambiente de pruebas (sandbox): tarjeta, Nequi y PSE. El flujo es real, pero no se mueve plata.
- **Envíos con seguimiento:** número de guía y línea de tiempo con cada cambio de estado.
- "Mis pedidos": el cliente ve el estado de su pago y de su envío.

### 3.4 Administración y reportes

- CRUD de motos y de accesorios. Las tres marcas son fijas (no hay CRUD de marcas).
- Parámetros de costo: precio del galón, tarifas del SOAT y porcentaje de impuesto.
- Gestión de envíos: el administrador avanza el estado de cada envío.
- **Radar de demanda (DuckDB):** cruza lo que la gente busca con el inventario. Ejemplo: "40 personas buscaron moto A2 con cuota menor a 300.000 y solo hay una en stock".
- **Reporte de ventas de accesorios (DuckDB):** por categoría y por semana.

## 4. Prioridades

| Prioridad | Qué entra |
| --- | --- |
| Obligatorio | Catálogo, buscar por cuota, costo real y modo trabajo, cotización y test drive con asesor y código de seguimiento, panel del asesor con estados y cola, login con 3 roles, tienda de accesorios con carrito, pago con Wompi sandbox, pedidos y envíos con seguimiento, CRUD del administrador |
| Ligero | Radar de demanda y reporte de ventas con DuckDB, TRM informativa con circuit breaker, comparador por costo real, accesorios compatibles por moto, mutmut solo sobre el dominio |
| Solo si sobra tiempo | Candela Bot en Telegram, alertas "avísame cuando…", retoma de la moto usada, precio congelado con la TRM, pasaporte de la moto, asesor virtual con IA |
| Fuera de alcance | Venta o separación de motos en línea, cobros reales (solo sandbox), devoluciones y reembolsos, conexión con transportadoras reales (el envío es simulado), citas de taller |

Si falta tiempo, se recorta en este orden: comparador, accesorios compatibles, reporte de ventas.

## 5. Reglas de negocio

| Código | Regla |
| --- | --- |
| RN-01 | Solo se venden motos Honda, Kawasaki y Yamaha. |
| RN-02 | Una moto es categoría A1 si tiene hasta 125 cc y A2 si tiene más. Con licencia A1 solo se muestran motos A1. |
| RN-03 | La cuota se calcula con la fórmula de cuota fija: `cuota = P · i / (1 − (1 + i)^(−n))`. La búsqueda por cuota usa la misma fórmula despejando `P`. |
| RN-04 | Al cotizar o pedir un test drive se asigna el asesor de esa marca que tenga menos atenciones abiertas. |
| RN-05 | Cada cotización y test drive tiene un código de seguimiento único con el formato `CM-XXXX`. |
| RN-06 | El total de un pedido siempre lo calcula el backend con los precios de la base de datos. Nunca se usa el total que manda el navegador. |
| RN-07 | Al crear un pedido, el stock queda reservado 15 minutos. Si no se paga en ese tiempo, el pedido pasa a `EXPIRADO` y el stock se libera. |
| RN-08 | El envío solo se crea cuando el pago queda `APROBADO`. |
| RN-09 | Un aviso de Wompi sin firma válida se ignora. Si el mismo aviso llega dos veces, se procesa una sola vez. |
| RN-10 | Un cliente solo puede ver sus propios pedidos, direcciones y cotizaciones. |
| RN-11 | El costo y los días de envío dependen del departamento de destino. |
| RN-12 | Las contraseñas se guardan con hash (bcrypt), nunca en texto plano. |

## 6. Estados

| Entidad | Estados |
| --- | --- |
| Atención (cotización) | `NUEVO`, `CONTACTADO`, `TEST_DRIVE`, `NEGOCIANDO`, `VENDIDO`, `DESCARTADO` |
| Test drive | `PENDIENTE`, `PROGRAMADO`, `REALIZADO`, `CANCELADO` |
| Pedido | `PENDIENTE_PAGO`, `PAGADO`, `EXPIRADO` |
| Pago | `PENDIENTE`, `APROBADO`, `RECHAZADO`, `ERROR` |
| Envío | `PREPARANDO`, `ENVIADO`, `EN_CAMINO`, `ENTREGADO` |

Un pedido puede tener varios intentos de pago (si el primero es rechazado). Cuando el pedido queda `PAGADO`, el avance del despacho se ve en el estado del envío.

## 7. Modelo de datos (propuesta; Laura la ajusta en el MER)

| Tabla | Columnas propuestas |
| --- | --- |
| `marcas` | id, nombre, color_hex, descripcion |
| `motos` | id, marca_id, modelo, anio, cilindraje_cc, tipo, categoria_licencia, precio_cop, stock, consumo_km_galon, costo_mantenimiento_km_cop, descripcion, imagen_url |
| `parametros_costo` | id, precio_galon_cop, porcentaje_impuesto, actualizado_en |
| `tarifas_soat` | id, cilindraje_min, cilindraje_max, valor_anual_cop |
| `busquedas` | id, fecha, cuota_maxima_cop, cuota_inicial_cop, categoria_licencia, uso, marca_id, cantidad_resultados |
| `usuarios` | id, nombre, correo, telefono, hash_contrasena, rol, marca_especialidad_id (solo asesores) |
| `clientes` | id, nombre, correo, telefono, usuario_id (si tiene cuenta) |
| `cotizaciones` | id, codigo_seguimiento, cliente_id, moto_id, asesor_id, fecha, precio_cop, cuota_inicial_cop, plazo_meses, tasa_mensual, cuota_mensual_cop, estado_atencion |
| `test_drives` | id, codigo_seguimiento, cliente_id, moto_id, asesor_id, fecha_solicitud, fecha_programada, estado |
| `accesorios` | id, sku, nombre, categoria, descripcion, precio_cop, stock, imagen_url |
| `compatibilidades` | accesorio_id, moto_id (llave compuesta) |
| `departamentos` | codigo, nombre, costo_envio_cop, dias_envio |
| `municipios` | codigo, nombre, departamento_codigo |
| `direcciones` | id, usuario_id, municipio_codigo, detalle, telefono_contacto |
| `pedidos` | id, usuario_id, direccion_id, estado, subtotal_cop, costo_envio_cop, total_cop, creado_en, reservado_hasta |
| `items_pedido` | id, pedido_id, accesorio_id, cantidad, precio_unitario_cop |
| `pagos` | id, pedido_id, referencia, transaccion_id, metodo, estado, monto_cop, creado_en, actualizado_en |
| `eventos_pago` | id, pago_id, checksum (único), estado_recibido, recibido_en |
| `envios` | id, pedido_id, numero_guia, costo_cop, estado, creado_en |
| `eventos_envio` | id, envio_id, estado, fecha, nota |

Relaciones principales: una marca tiene muchas motos; un asesor atiende muchas cotizaciones y test drives; un cliente tiene muchas cotizaciones y test drives; un accesorio sirve para muchas motos y una moto acepta muchos accesorios (muchos a muchos); un usuario tiene muchas direcciones y muchos pedidos; un pedido tiene muchos ítems, muchos intentos de pago y un envío; un envío tiene muchos eventos.

## 8. API (propuesta; Nicolás la ajusta)

| Acceso | Endpoints |
| --- | --- |
| Público | `GET /marcas` · `GET /motos` · `GET /motos/{id}` · `GET /motos/por-cuota` · `GET /motos/{id}/costo-real` · `GET /motos/comparar` · `GET /trm` · `POST /cotizaciones` · `POST /test-drives` · `GET /seguimiento/{codigo}` · `GET /accesorios` · `GET /accesorios/{id}` · `GET /departamentos` · `GET /departamentos/{codigo}/municipios` · `GET /envios/tarifa` · `POST /auth/registro` · `POST /auth/login` |
| Solo Wompi | `POST /pagos/webhook` (valida la firma) |
| Cliente | `GET` y `POST /mis-direcciones` · `POST /pedidos` · `GET /mis-pedidos` · `GET /mis-pedidos/{id}` · `POST /mis-pedidos/{id}/verificar-pago` · `GET /mis-cotizaciones` |
| Asesor | `GET /asesor/atenciones` · `PATCH /cotizaciones/{id}/estado` · `GET /asesor/test-drives` · `POST /asesor/test-drives/siguiente` |
| Administrador | `POST`, `PUT` y `DELETE` de `/motos` y `/accesorios` · `GET` y `PUT /parametros-costo` · `GET /admin/pedidos` · `PATCH /envios/{id}/estado` · `GET /reportes/demanda` · `GET /reportes/ventas` |

## 9. Cómo funciona una compra de accesorios

1. El cliente confirma el carrito con `POST /pedidos`. La API recalcula el total, reserva el stock y crea el pedido en `PENDIENTE_PAGO` con un pago `PENDIENTE` y una referencia única.
2. Angular abre el widget de Wompi con esa referencia. El cliente paga con tarjeta, Nequi o PSE. Los datos de la tarjeta nunca pasan por nuestro servidor.
3. Wompi avisa el resultado a `POST /pagos/webhook`. La API revisa la firma (checksum SHA256 con el secreto de eventos) y que el aviso no esté repetido.
4. Si el pago queda `APROBADO`, el pedido pasa a `PAGADO`, se crea el envío con su número de guía y el primer evento `PREPARANDO`.
5. Si el pago es rechazado, el cliente puede intentar otra vez mientras dure la reserva. Si pasan 15 minutos sin pago, el pedido queda `EXPIRADO` y el stock vuelve.
6. Respaldo: cuando el cliente vuelve del widget, la API también le pregunta a Wompi el estado de la transacción (`POST /mis-pedidos/{id}/verificar-pago`). Así funciona aunque el aviso no llegue.

## 10. Integraciones externas

| Servicio | Para qué | Notas |
| --- | --- | --- |
| Wompi (sandbox) | Pago de accesorios | API de pruebas: `https://sandbox.wompi.co/v1`. Llaves de prueba con prefijo `pub_test_` y `prv_test_`. Para que el aviso llegue a un computador local se usa un túnel (ngrok o Cloudflare Tunnel). |
| datos.gov.co: TRM | Precio de referencia en dólares | `https://www.datos.gov.co/resource/32sa-8pi3.json?$limit=1&$order=vigenciahasta DESC`. Con circuit breaker. |
| datos.gov.co: DIVIPOLA (DANE) | Departamentos y municipios para las direcciones | Se carga una sola vez en la base de datos con un script. |

Las llaves de Wompi van en el archivo `.env`, nunca en el repositorio. Las variables están documentadas en `backend/.env.example`.

## 11. Estructuras de datos propias (tema de la sesión 3)

| Estructura | Dónde se usa |
| --- | --- |
| Cola FIFO con nodos enlazados (`ColaTestDrives`) | Una cola de test drives por asesor |
| Pila (`PilaSimulaciones`) | Deshacer en el simulador de crédito |
| Árbol binario de búsqueda (`ArbolMotosPorPrecio`) | Buscar por cuota: motos dentro de un rango de precio |

## 12. Reparto

| Integrante | Responsabilidad |
| --- | --- |
| Andrés | Arquitectura, capa de dominio (entidades, reglas, excepciones, puertos, pila y árbol), frontend completo en Angular, revisión de PRs |
| Laura | Modelo entidad-relación, modelos SQLAlchemy, repositorios, datos de prueba y carga de DIVIPOLA, cola de test drives, transacción de compra y reserva de stock, reportes con DuckDB, cobertura y mutmut |
| Nicolás | Requisitos y wireframes, casos de uso y endpoints, registro y login con JWT y roles, integración con Wompi (webhook y verificación), envíos, TRM con circuit breaker, Docker |
