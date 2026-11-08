1. Requisitos Funcionales (RF)
Módulo: Motos y Costo Real
RF-01: Búsqueda y filtrado de motos por capacidad financiera y categoría de licencia

Descripción: El sistema debe calcular el precio máximo financiable mediante la fórmula de amortización fija francesa y retornar exclusivamente las motocicletas compatibles con dicho presupuesto y la categoría de licencia del usuario.

Reglas asociadas: RN-01, RN-02, RN-03.

Entradas: Cuota mensual máxima (int), cuota inicial (int), plazo en meses (int), categoría de licencia (A1 o A2) y opcionalmente marca (Honda, Kawasaki, Yamaha).

Salida: Lista de motocicletas cuyo precio de venta sea menor o igual al capital máximo calculado. Si el usuario selecciona licencia A1, solo deben retornarse motocicletas de cilindraje menor o igual a 125 cc.

RF-02: Estimación de costo real mensual y simulación en modo trabajo

Descripción: El sistema debe calcular el costo operativo mensual total de una motocicleta seleccionada integrando cuota crediticia estimada, consumo de combustible, SOAT, mantenimiento proyectado e impuestos.

Reglas asociadas: RN-03.

Entradas: Identificador de la moto (moto_id), kilómetros promedio mensuales (km_mes), tipo de uso (urbano/mixto), cuota inicial, plazo y parámetros opcionales de modo trabajo (ganancia neta diaria esperada y días trabajados por mes).

Salida: Desglose mensual detallado en pesos colombianos (COP) y, en modo trabajo, el retorno de inversión indicando el número estimado de meses requeridos para amortizar el vehículo.

RF-03: Visualización de catálogo y detalle con conversión de divisa en paralelo

Descripción: El sistema debe presentar el catálogo de motocicletas permitiendo consultar la ficha técnica individual y su precio de referencia en dólares estadounidenses (USD) de forma simultánea.

Reglas asociadas: RN-01.

Entradas: Identificador de la moto (moto_id).

Salida: Datos técnicos del vehículo, galería multimedia por marca y precio en COP junto al equivalente calculado en USD a partir de la TRM del día obtenida de manera concurrente.

Módulo: Atención Personalizada
RF-04: Generación de cotización con asignación balanceada de asesor especialista

Descripción: El sistema debe registrar solicitudes de cotización formal, asociar automáticamente un asesor comercial especialista en la marca elegida con menor carga activa y emitir un código alfanumérico único de atención.

Reglas asociadas: RN-01, RN-04, RN-05.

Entradas: Datos de contacto del solicitante (nombre, correo, teléfono), moto_id, cuota inicial y plazo.

Salida: Registro de cotización generado en estado NUEVO, enlace directo de contacto hacia la línea de WhatsApp del asesor asignado y código de seguimiento único con formato CM-XXXX.

RF-05: Agendamiento y gestión de turnos para prueba de manejo (Test Drive)

Descripción: El sistema debe permitir a cualquier visitante solicitar una prueba de manejo para un modelo específico, incorporando la solicitud en la cola de turnos del asesor correspondiente según su carga laboral.

Reglas asociadas: RN-04, RN-05.

Entradas: Datos del solicitante, número de licencia de conducción, fecha preferencial, sede y moto_id.

Salida: Registro del test drive en estado PENDIENTE encolado para el asesor especialista, y código de seguimiento CM-XXXX retornado al usuario.

RF-06: Consulta pública de trazabilidad mediante código de seguimiento

Descripción: El sistema debe permitir la consulta pública e inmediata del estado actual de una cotización o prueba de manejo mediante el ingreso de su identificador alfanumérico, sin exigir inicio de sesión previo.

Reglas asociadas: RN-05.

Entradas: Código de seguimiento (CM-XXXX).

Salida: Estado de la atención (NUEVO, CONTACTADO, TEST_DRIVE, NEGOCIANDO, VENDIDO, DESCARTADO) o del test drive (PENDIENTE, PROGRAMADO, REALIZADO, CANCELADO), nombre del asesor asignado y marca consultada.

Módulo: Tienda de Accesorios y Pagos
RF-07: Creación de pedido con reserva transaccional de inventario y cálculo de envío

Descripción: El sistema debe validar la disponibilidad de existencias, bloquear el stock correspondiente durante 15 minutos exactos y consolidar el monto total del pedido en el backend a partir de los precios oficiales de la base de datos y la tarifa del departamento de destino.

Reglas asociadas: RN-06, RN-07, RN-10, RN-11.

Entradas: Token de autenticación del cliente, listado de ítems (accesorio_id, cantidad) y dirección de entrega (municipio_id, departamento).

Salida: Registro del pedido en estado PENDIENTE_PAGO, bloqueo de inventario con expiración a 15 minutos, registro de pago PENDIENTE, desglose de costos (subtotal accesorios + costo envío departamental) y parámetros firmados para inicializar el widget de Wompi.

RF-08: Procesamiento asíncrono e idempotente de eventos de pago (Webhook Wompi)

Descripción: El sistema debe recibir notificaciones de transacciones emitidas por la pasarela de pagos Wompi, validar su integridad criptográfica y actualizar el estado de los pedidos evitando procesamiento duplicado.

Reglas asociadas: RN-08, RN-09.

Entradas: Payload JSON del evento transaction.updated junto con checksum SHA-256 en cabecera o propiedad de firma.

Salida: Transición del pago a APROBADO o RECHAZADO. Si es aprobado, transición inmediata del pedido a PAGADO y generación del registro de envío; si es rechazado, conservación del estado para reintento dentro del plazo de reserva. Retorno HTTP 200 para eventos repetidos previamente procesados.

RF-09: Expiración automática y liberación de existencias por reserva vencida

Descripción: El sistema debe contar con un proceso en segundo plano que identifique de forma periódica aquellos pedidos que superen el límite de 15 minutos sin confirmación de pago aprobada.

Reglas asociadas: RN-07.

Entradas: Marca de tiempo actual y registros de pedidos en estado PENDIENTE_PAGO.

Salida: Actualización del pedido al estado EXPIRADO y restitución automática de las unidades al inventario disponible de cada accesorio involucrado.

Módulo: Administración y Reportes
RF-10: Generación analítica de radar de demanda e inventario con DuckDB

Descripción: El sistema debe proporcionar a los administradores métricas analíticas comparativas entre las búsquedas de motocicletas realizadas por los visitantes y el inventario real disponible en el concesionario.

Reglas asociadas: N/A (Módulo de Analítica).

Entradas: Parámetros de rango de fechas y filtros de marca/cilindraje solicitados por un usuario con rol ADMIN.

Salida: Métricas agregadas generadas mediante consultas OLAP en DuckDB con volumen de búsquedas por cuota, relación demanda vs. stock y modelos con mayor tasa de cotización.

2. Requisitos No Funcionales (RNF)
RNF-01 (Seguridad - Cifrado de Credenciales): El sistema debe almacenar todas las contraseñas de los usuarios utilizando el algoritmo de derivación de claves bcrypt con un factor de trabajo (cost factor) no menor a 12 rondas de salting, garantizando que ninguna credencial resida en texto claro en reposo ni en memoria persistida.

Regla asociada: RN-12.

RNF-02 (Seguridad - Autenticación y Autorización RBAC): El sistema debe gestionar el acceso mediante tokens de autenticación JSON Web Tokens (JWT) firmados criptográficamente mediante algoritmo HMAC-SHA256, con tiempo de caducidad estricto (JWT_EXPIRA_MINUTOS) y control de acceso basado en roles (CLIENTE, ASESOR, ADMIN) para cada endpoint de la API.

RNF-03 (Seguridad - Mitigación BOLA / OWASP API1): La API debe implementar validación de propiedad a nivel de objeto en todas las rutas bajo el prefijo /mis-... y operaciones sobre cotizaciones. Si un usuario intenta acceder o modificar un recurso que no le pertenece, el sistema debe responder con código HTTP 404 Not Found en lugar de 403 Forbidden, impidiendo la enumeración de recursos no autorizados.

Regla asociada: RN-10.

RNF-04 (Seguridad - Integridad de Webhooks e Idempotencia): El endpoint receptor del webhook de Wompi debe recalcular el checksum SHA-256 concatenando las propiedades requeridas de la transacción con el secreto de eventos (WOMPI_SECRETO_EVENTOS). Si la firma no coincide, debe rechazar la solicitud con HTTP 401 Unauthorized. Las solicitudes con transacciones ya procesadas deben retornar HTTP 200 OK sin alterar el estado del pedido.

Regla asociada: RN-09.

RNF-05 (Disponibilidad y Resiliencia - Circuit Breaker): La integración con la API de datos abiertos para la consulta de la TRM debe operar de manera asíncrona mediante un cliente HTTP no bloqueante y estar protegida por un patrón Circuit Breaker de tres estados (Cerrado, Abierto, Semiabierto). Ante caídas consecutivas del servicio externo, el circuito debe abrirse inmediatamente y responder con el último valor en caché o degradar la visualización a pesos colombianos sin interrumpir el flujo.

RNF-06 (Rendimiento - Latencia de Respuestas): El backend debe resolver el 95% de las peticiones de lectura del catálogo y consultas de costo real en un tiempo de respuesta inferior a 300 milisegundos bajo condiciones de concurrencia regular, recurriendo a asyncio.gather para la ejecución simultánea de consultas independientes.

RNF-07 (Usabilidad y Accesibilidad - Principios Heurísticos de Nielsen): La interfaz de usuario debe satisfacer las heurísticas de visibilidad del estado del sistema y coherencia, utilizando un código visual por fabricante: Rojo para Honda, Verde para Kawasaki y Azul para Yamaha, manteniendo elementos de ayuda contextual y mensajes claros ante errores de validación.

Regla asociada: RN-01.

RNF-08 (Mantenibilidad - Arquitectura Hexagonal y DDD): El backend debe respetar de forma estricta la separación arquitectónica Hexagonal (Puertos y Adaptadores). La capa de dominio (domain) no debe poseer dependencias de frameworks web (FastAPI), bases de datos (SQLAlchemy) ni librerías externas. La lógica de negocio debe encapsularse en entidades, servicios de dominio y casos de uso acoplados únicamente a interfaces abstractas (abc.ABC).

RNF-09 (Portabilidad - Aislamiento en Contenedores): El sistema completo debe ser desplegable en entornos Linux/macOS/Windows mediante contenedores Docker y orquestación con docker-compose, separando el servicio de backend (Uvicorn), el frontend (Nginx) y persistiendo la base de datos relacional a través de volúmenes de almacenamiento.

RNF-10 (Calidad de Código y Pruebas Automatizadas): El código base debe cumplir con la especificación de estilo y análisis estático de ruff con un límite estricto de 100 caracteres por línea y tipado estático verificado. Los casos de uso y la lógica de dominio deben alcanzar cobertura de pruebas unitarias automatizadas con pytest.


---

## 3. Historias de Usuario (HU)

### HU-01: Búsqueda de motos según capacidad de pago mensual
* **Como:** Visitante del concesionario web.
* **Quiero:** Filtrar el catálogo de motos ingresando cuánto dinero puedo pagar cada mes y qué licencia de conducción tengo.
* **Para:** Conocer qué opciones se ajustan a mi bolsillo sin tener que revisar modelos fuera de mi presupuesto ni de mi habilitación legal.
* **Prioridad:** Alta (Obligatorio).
* **Reglas de Negocio:** RN-01, RN-02, RN-03.

**Criterios de Aceptación:**
* **Escenario 1: Filtrado exitoso para conductor con licencia A1**
  * **Dado** que un visitante ingresa una cuota mensual máxima de $350.000 COP, un plazo de 36 meses y una cuota inicial de $1.000.000 COP.
  * **Y** selecciona que posee licencia de conducción categoría "A1".
  * **Cuando** solicita la búsqueda de motocicletas.
  * **Entonces** el sistema calcula el precio máximo de adquisición mediante la fórmula de amortización fija.
  * **Y** muestra únicamente motos de las marcas Honda, Kawasaki o Yamaha cuyo valor total sea igual o menor a dicho capital y cuyo cilindraje no exceda los 125 cc (cumpliendo RN-01 y RN-02).
* **Escenario 2: Restricción de modelos con licencia A1**
  * **Dado** que existen motocicletas en catálogo con cilindraje de 150 cc o superior cuyo precio encaja en la cuota del usuario.
  * **Cuando** el usuario busca con licencia "A1" seleccionada.
  * **Entonces** el sistema omite dichos modelos del listado de resultados (cumpliendo RN-02).

---

### HU-02: Simulación de costo real mensual y modo trabajo
* **Como:** Visitante interesado en adquirir una moto para transporte personal o trabajo.
* **Quiero:** Calcular el costo total mensual proyectado (combustible, seguro, impuestos y mantenimiento) e ingresar parámetros de ingresos por domicilio si elijo modo trabajo.
* **Para:** Evaluar si el vehículo es financieramente sostenible con mis ingresos diarios proyectados.
* **Prioridad:** Alta (Obligatorio).
* **Reglas de Negocio:** RN-03.

**Criterios de Aceptación:**
* **Escenario 1: Cálculo estándar de costo de posesión**
  * **Dado** que el usuario visualiza el detalle de una motocicleta.
  * **Cuando** ingresa un estimado de 800 km recorridos por mes y un plan de crédito de 24 cuotas.
  * **Entonces** el sistema calcula y muestra el costo total mensual consolidado sumando la cuota crediticia, la proporción mensual del SOAT, el impuesto vehicular, el mantenimiento preventivo y el gasto de combustible proyectado.
* **Escenario 2: Activación del cálculo para modo trabajo**
  * **Dado** que el usuario activa la casilla de "Modo Trabajo".
  * **Cuando** digita una ganancia neta diaria estimada de $80.000 COP y 26 días laborales al mes.
  * **Entonces** el sistema descuenta el costo real mensual del ingreso proyectado y presenta el flujo neto mensual restante y la estimación de meses requeridos para recuperar la inversión total del vehículo.

---

### HU-03: Solicitud de cotización con asignación de asesor de marca
* **Como:** Visitante interesado en comprar una motocicleta.
* **Quiero:** Enviar mis datos de contacto para cotizar un modelo sin necesidad de registrar una cuenta.
* **Para:** Recibir asesoría comercial experta en la marca de la moto y poder hacer seguimiento directo.
* **Prioridad:** Alta (Obligatorio).
* **Reglas de Negocio:** RN-01, RN-04, RN-05.

**Criterios de Aceptación:**
* **Escenario 1: Asignación balanceada de asesor especialista**
  * **Dado** que existen dos asesores registrados para la marca "Yamaha", uno con 4 atenciones activas y otro con 2 atenciones activas.
  * **Cuando** un visitante completa el formulario de cotización para una moto Yamaha.
  * **Entonces** el sistema asigna la cotización al asesor con 2 atenciones activas (cumpliendo RN-04).
  * **Y** genera un código de seguimiento único con estructura `CM-XXXX` (cumpliendo RN-05).
  * **Y** presenta en pantalla el nombre del asesor junto con un enlace dinámico directo a su WhatsApp.

---

### HU-04: Consulta de estado de atención mediante código único
* **Como:** Visitante que radicó una cotización o solicitud de test drive.
* **Quiero:** Ingresar mi código de seguimiento en la web.
* **Para:** Conocer el estado actual del trámite sin tener que iniciar sesión ni llamar al concesionario.
* **Prioridad:** Alta (Obligatorio).
* **Reglas de Negocio:** RN-05.

**Criterios de Aceptación:**
* **Escenario 1: Consulta de código válido**
  * **Dado** que un usuario ingresa a la vista pública de seguimiento.
  * **Cuando** digita un código existente con formato `CM-1042`.
  * **Entonces** el sistema retorna el estado de avance (`NUEVO`, `CONTACTADO`, `TEST_DRIVE`, `NEGOCIANDO`, `VENDIDO` o `DESCARTADO`), la fecha de registro y la marca de interés.
* **Escenario 2: Consulta de código inexistente**
  * **Dado** que un usuario digita un código `CM-9999` que no está en la base de datos.
  * **Cuando** presiona el botón de consulta.
  * **Entonces** el sistema retorna un error HTTP 404 e informa que el código ingresado no existe.

---

### HU-05: Gestión de cola de atenciones y turnos del asesor
* **Como:** Asesor comercial de Candela Motors.
* **Quiero:** Visualizar mis cotizaciones asignadas y avanzar la cola de mis solicitudes de test drive.
* **Para:** Contactar a los clientes interesados y registrar el progreso del ciclo de ventas.
* **Prioridad:** Alta (Obligatorio).
* **Reglas de Negocio:** RN-04, RN-10.

**Criterios de Aceptación:**
* **Escenario 1: Visualización exclusiva de asignaciones propias**
  * **Dado** que un usuario con rol `ASESOR` ha iniciado sesión.
  * **Cuando** consulta su panel de atenciones.
  * **Entonces** el sistema lista únicamente las cotizaciones asignadas a su identificador de asesor, organizadas por estado.
* **Escenario 2: Restricción de modificación de atención ajena**
  * **Dado** que el asesor autenticado intenta enviar una petición PATCH para modificar el estado de una cotización asignada a otro asesor.
  * **Cuando** el servidor evalúa la solicitud.
  * **Entonces** el sistema rechaza la operación respondiendo `HTTP 404 Not Found` (cumpliendo RN-10 y mitigando BOLA).

---

### HU-06: Registro e inicio de sesión de clientes con protección de identidad
* **Como:** Comprador de accesorios.
* **Quiero:** Registrar una cuenta personal y autenticarme con correo y contraseña.
* **Para:** Guardar mis direcciones de despacho y realizar compras virtuales seguras.
* **Prioridad:** Alta (Obligatorio).
* **Reglas de Negocio:** RN-10, RN-12.

**Criterios de Aceptación:**
* **Escenario 1: Registro con hash de contraseña**
  * **Dado** que un nuevo cliente envía sus datos mediante `POST /auth/registro`.
  * **Cuando** el backend procesa la petición.
  * **Entonces** almacena la clave bajo un hash seguro generado con bcrypt (cumpliendo RN-12).
  * **Y** la respuesta omite cualquier campo relacionado con el hash de la contraseña.
* **Escenario 2: Autenticación exitosa y emisión de JWT**
  * **Dado** que el cliente envía credenciales válidas en `POST /auth/login`.
  * **Cuando** la verificación de contraseña con bcrypt es satisfactoria.
  * **Entonces** el backend responde un token JWT con el id del usuario, el rol `CLIENTE` y una marca de expiración (`exp`) estricta.

---

### HU-07: Creación de pedido y pago con reserva temporal de stock
* **Como:** Cliente registrado autenticado.
* **Quiero:** Enviar mi carrito de accesorios a la pasarela de pagos Wompi.
* **Para:** Cancelar mi pedido de forma segura mediante Nequi, PSE o tarjeta sin perder las unidades mientras pago.
* **Prioridad:** Alta (Obligatorio).
* **Reglas de Negocio:** RN-06, RN-07, RN-11.

**Criterios de Aceptación:**
* **Escenario 1: Reserva de inventario y cálculo de precio en servidor**
  * **Dado** que un cliente autenticado tiene artículos en su carrito y selecciona una dirección de envío en Antioquia.
  * **Cuando** ejecuta `POST /pedidos`.
  * **Entonces** el backend calcula el total con los precios de la base de datos (ignorando cualquier valor enviado por el cliente, cumpliendo RN-06).
  * **Y** suma la tarifa de flete correspondiente al departamento de destino (cumpliendo RN-11).
  * **Y** descuenta transaccionalmente el stock reservándolo por 15 minutos exactos con estado de pedido `PENDIENTE_PAGO` (cumpliendo RN-07).
  * **Y** retorna la referencia y la firma de integridad para abrir el widget de Wompi en centavos COP.

---

### HU-08: Confirmación de pago mediante Webhook de Wompi y alta de envío
* **Como:** Sistema de Candela Motors.
* **Quiero:** Recibir y autenticar la notificación asíncrona de Wompi.
* **Para:** Confirmar el pedido pagado e iniciar automáticamente el proceso logístico de despacho.
* **Prioridad:** Alta (Obligatorio).
* **Reglas de Negocio:** RN-08, RN-09.

**Criterios de Aceptación:**
* **Escenario 1: Transacción aprobada con firma válida**
  * **Dado** que Wompi envía una notificación a `POST /pagos/webhook` con estado `APPROVED`.
  * **Cuando** el backend valida que el hash SHA-256 coincide con el secreto del comercio (`WOMPI_SECRETO_EVENTOS`).
  * **Entonces** el pedido cambia a estado `PAGADO`.
  * **Y** se genera automáticamente la orden de envío con número de guía y evento inicial `PREPARANDO` (cumpliendo RN-08 y RN-09).
* **Escenario 2: Notificación con firma inválida o adulterada**
  * **Dado** que un atacante envía una petición con un checksum incorrecto hacia `/pagos/webhook`.
  * **Cuando** el backend recalcula la firma de integridad.
  * **Entonces** rechaza la petición con `HTTP 401 Unauthorized` sin alterar el pedido ni crear envíos (cumpliendo RN-09).
* **Escenario 3: Notificación de evento duplicado (Idempotencia)**
  * **Dado** que un evento ya aprobado es enviado nuevamente por Wompi.
  * **Cuando** el backend verifica que el identificador de la transacción ya fue procesado.
  * **Entonces** responde `HTTP 200 OK` inmediatamente sin alterar el inventario ni duplicar la guía de envío.

---

### HU-09: Seguimiento de línea de tiempo del pedido y despacho
* **Como:** Cliente que realizó una compra de accesorios.
* **Quiero:** Entrar a la sección "Mis Pedidos" y ver la trazabilidad de mi paquete.
* **Para:** Saber en qué etapa de preparación o transporte se encuentra mi orden.
* **Prioridad:** Alta (Obligatorio).
* **Reglas de Negocio:** RN-10.

**Criterios de Aceptación:**
* **Escenario 1: Consulta de pedido propio**
  * **Dado** que un cliente autenticado consulta `GET /mis-pedidos/{id}`.
  * **Cuando** el pedido pertenece a su ID de usuario.
  * **Entonces** visualiza la cronología completa de eventos del envío (`PREPARANDO` → `ENVIADO` → `EN_CAMINO` → `ENTREGADO`) con sus respectivas fechas y número de guía.
* **Escenario 2: Intento de visualización de pedido de otro cliente**
  * **Dado** que un cliente autenticado intenta consultar el detalle de un pedido perteneciente a un tercero.
  * **Cuando** el backend valida el identificador de usuario frente al token.
  * **Entonces** el sistema responde `HTTP 404 Not Found` (cumpliendo RN-10).

---

### HU-10: Gestión administrativa del ciclo de envíos
* **Como:** Administrador del concesionario.
* **Quiero:** Actualizar secuencialmente el estado de los paquetes en preparación.
* **Para:** Mantener informados a los compradores sobre el tránsito de sus accesorios.
* **Prioridad:** Alta (Obligatorio).
* **Reglas de Negocio:** RN-08.

**Criterios de Aceptación:**
* **Escenario 1: Transición hacia adelante exitosa**
  * **Dado** que un envío se encuentra en estado `PREPARANDO`.
  * **Cuando** el administrador envía `PATCH /envios/{id}/estado` indicando el nuevo estado `ENVIADO`.
  * **Entonces** el sistema registra el nuevo estado, anexa el evento a la línea de tiempo con marca de tiempo actual y responde `HTTP 200 OK`.
* **Escenario 2: Intento de regresión de estado inválida**
  * **Dado** que un envío ya se encuentra en estado `EN_CAMINO`.
  * **Cuando** el administrador intenta retroceder el estado a `PREPARANDO`.
  * **Entonces** el dominio rechaza la operación lanzando una excepción de negocio que la API transforma en `HTTP 409 Conflict`.
