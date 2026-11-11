# Especificación de Requisitos de Software: Candela Motors

---

## 1. Requisitos Funcionales (RF)

### Módulo 1: Motos y Costo Real

* **RF-01: Búsqueda y filtrado de motos por capacidad financiera y categoría de licencia**
  * **Descripción:** El sistema debe calcular el precio máximo financiable mediante la fórmula de amortización fija francesa y retornar las motocicletas de las marcas oficiales que se ajusten al presupuesto y a la categoría de licencia del usuario.
  * **Reglas asociadas:** RN-01, RN-02, RN-03.
  * **Entradas:** Cuota mensual máxima (`int`), cuota inicial (`int`), plazo en meses (`int`), categoría de licencia (`A1` o `A2`) y opcionalmente marca (`Honda`, `Kawasaki`, `Yamaha`).
  * **Salida:** Lista de motocicletas cuyo precio de venta sea menor o igual al capital máximo calculado. Si el usuario selecciona licencia `A1`, solo deben retornarse motocicletas de cilindraje menor o igual a 125 cc.

* **RF-02: Estimación de costo real mensual y simulación en modo trabajo**
  * **Descripción:** El sistema debe calcular el costo operativo mensual total de una motocicleta integrando cuota crediticia estimada, consumo de combustible según perfil de uso (`CIUDAD`, `CARRETERA`, `TRABAJO`), SOAT prorrateado, mantenimiento proyectado e impuesto vehicular.
  * **Reglas asociadas:** RN-03.
  * **Entradas:** Identificador de la moto (`moto_id`), kilómetros promedio mensuales (`km_mes`), perfil de uso (`CIUDAD`, `CARRETERA`, `TRABAJO`), cuota inicial, plazo y parámetros opcionales de modo trabajo (ganancia neta diaria esperada y días trabajados por mes).
  * **Salida:** Desglose mensual detallado en pesos colombianos (COP) y, si se activa modo trabajo, el balance neto mensual y la proyección de meses requeridos para recuperar la inversión.

* **RF-03: Visualización de catálogo y detalle con conversión de divisa en paralelo**
  * **Descripción:** El sistema debe presentar el catálogo de motocicletas y la ficha técnica individual con sus especificaciones, una única imagen principal (`imagen_url`) y el precio de referencia en dólares estadounidenses (USD) calculado de forma concurrente con la TRM vigente.
  * **Reglas asociadas:** RN-01.
  * **Entradas:** Identificador de la moto (`moto_id`).
  * **Salida:** Ficha técnica de la moto, enlace a imagen principal (`imagen_url`), precio oficial en COP y precio referencial en USD obtenido mediante consulta paralela a la TRM.

---

### Módulo 2: Atención Personalizada

* **RF-04: Generación de cotización con asignación balanceada de asesor especialista**
  * **Descripción:** El sistema debe registrar solicitudes de cotización formal, asociar automáticamente al asesor especialista de la marca que tenga la menor carga de atenciones abiertas y emitir un código de seguimiento alfanumérico único.
  * **Reglas asociadas:** RN-01, RN-04, RN-05.
  * **Entradas:** Datos de contacto del solicitante (nombre, correo, teléfono), `moto_id`, cuota inicial y plazo.
  * **Salida:** Registro de cotización en estado `NUEVO`, enlace de WhatsApp directo al asesor especialista asignado y código único con formato `CM-XXXX`.

* **RF-05: Agendamiento y gestión de turnos para prueba de manejo (Test Drive)**
  * **Descripción:** El sistema debe permitir a cualquier visitante solicitar una prueba de manejo para un modelo en catálogo, incorporando la solicitud en la cola de turnos FIFO del asesor especialista de la marca.
  * **Reglas asociadas:** RN-04, RN-05.
  * **Entradas:** Datos de contacto del solicitante (nombre, correo, teléfono), `moto_id` y fecha preferencial.
  * **Salida:** Registro del test drive en estado `PENDIENTE` en la cola del asesor y código de seguimiento único `CM-XXXX` para el usuario.

* **RF-06: Consulta pública de trazabilidad mediante código de seguimiento**
  * **Descripción:** El sistema debe permitir la consulta inmediata del estado de una cotización o test drive mediante el ingreso del código de seguimiento, sin requerir registro ni inicio de sesión.
  * **Reglas asociadas:** RN-05.
  * **Entradas:** Código de seguimiento (`CM-XXXX`).
  * **Salida:** Estado de la atención (`NUEVO`, `CONTACTADO`, `TEST_DRIVE`, `NEGOCIANDO`, `VENDIDO`, `DESCARTADO`) o del test drive (`PENDIENTE`, `PROGRAMADO`, `REALIZADO`, `CANCELADO`), nombre del asesor asignado y marca consultada.

* **RF-07: Gestión de atenciones y turnos por parte del Asesor**
  * **Descripción:** El sistema debe permitir a un usuario con rol `ASESOR` consultar las cotizaciones que tiene asignadas, avanzar el estado de la atención en su embudo y desencolar el siguiente turno de su lista de test drives.
  * **Reglas asociadas:** RN-04, RN-10.
  * **Entradas:** Token de autenticación de asesor, `cotizacion_id`, nuevo estado de atención (`CONTACTADO`, `TEST_DRIVE`, `NEGOCIANDO`, `VENDIDO`, `DESCARTADO`).
  * **Salida:** Estado de atención actualizado y datos de la siguiente prueba de manejo a atender de su cola.

---

### Módulo 3: Tienda de Accesorios y Envíos

* **RF-08: Catálogo de accesorios y compatibilidad por modelo de moto**
  * **Descripción:** El sistema debe listar los accesorios disponibles permitiendo filtrar por categoría y por compatibilidad con modelos específicos de moto.
  * **Reglas asociadas:** N/A (Tienda).
  * **Entradas:** Parámetros de consulta opcionales: categoría de accesorio y `moto_id`.
  * **Salida:** Lista de accesorios disponibles con nombre, descripción, precio en COP, stock actual, `imagen_url` y lista de motos compatibles.

* **RF-09: Carrito de compras y gestión de direcciones del cliente (DIVIPOLA)**
  * **Descripción:** El sistema debe permitir al cliente autenticado agregar accesorios a un carrito de compras y registrar múltiples direcciones de entrega validadas contra los departamentos y municipios oficiales de Colombia (DANE / DIVIPOLA).
  * **Reglas asociadas:** RN-10, RN-11.
  * **Entradas:** Token de cliente, datos de dirección (departamento, municipio, nomenclatura, barrio, código postal).
  * **Salida:** Direcciones guardadas asociadas al perfil del cliente y consulta de tarifas de envío según el departamento seleccionado.

* **RF-10: Creación de pedido con dirección guardada y reserva de inventario**
  * **Descripción:** El sistema debe validar stock, calcular el costo total oficial en el backend sumando el flete departamental, reservar existencias por 15 minutos exactos y crear el pedido a partir de una dirección guardada del cliente.
  * **Reglas asociadas:** RN-06, RN-07, RN-10, RN-11.
  * **Entradas:** Token de autenticación del cliente, listado de ítems (`accesorio_id`, `cantidad`) y `direccion_id` guardada previamente.
  * **Salida:** Pedido en estado `PENDIENTE_PAGO`, bloqueo de inventario con vencimiento a 15 minutos, registro de pago `PENDIENTE` y datos cifrados para inicializar el widget de Wompi.

* **RF-11: Procesamiento asíncrono e idempotente de avisos de Wompi (Webhook)**
  * **Descripción:** El sistema debe recibir avisos de pago de Wompi, validar su firma criptográfica SHA-256 e ignorar eventos duplicados mediante el registro del checksum del evento.
  * **Reglas asociadas:** RN-08, RN-09.
  * **Entradas:** Payload JSON del evento `transaction.updated` y firma SHA-256.
  * **Salida:** Si el pago es `APROBADO`, el pedido pasa a `PAGADO` y se genera el registro de envío con evento `PREPARANDO`. Si es rechazado, se conserva el pedido para reintento. Si el evento ya fue procesado (mismo checksum), retorna HTTP 200 sin reprocesar.

* **RF-12: Expiración automática y liberación de existencias por reserva vencida**
  * **Descripción:** El sistema debe ejecutar una tarea en segundo plano que identifique pedidos con más de 15 minutos en `PENDIENTE_PAGO` sin confirmación de pago.
  * **Reglas asociadas:** RN-07.
  * **Entradas:** Marca de tiempo actual y registros de pedidos pendientes.
  * **Salida:** Transición de pedidos a `EXPIRADO` y retorno automático de las cantidades al stock disponible.

* **RF-13: Gestión y avance de envíos por el Administrador**
  * **Descripción:** El sistema debe permitir a un usuario con rol `ADMIN` consultar todos los pedidos y avanzar secuencialmente el estado del despacho (`PREPARANDO` → `ENVIADO` → `EN_CAMINO` → `ENTREGADO`).
  * **Reglas asociadas:** RN-08.
  * **Entradas:** Token de administrador, `envio_id` y nuevo estado del envío.
  * **Salida:** Estado de envío actualizado y nuevo registro histórico incorporado a la línea de tiempo de seguimiento.

---

### Módulo 4: Autenticación, Administración y Analítica

* **RF-14: Registro y autenticación de usuarios con control de acceso RBAC**
  * **Descripción:** El sistema debe permitir el autoregistro de clientes y el inicio de sesión para todos los roles (`CLIENTE`, `ASESOR`, `ADMIN`) emitiendo un token JWT firmado.
  * **Reglas asociadas:** RN-10, RN-12.
  * **Entradas:** Datos de registro (nombre, correo, teléfono, contraseña) o credenciales de acceso (correo, contraseña).
  * **Salida:** Creación del usuario con rol `CLIENTE` o token JWT con rol correspondiente y tiempo de expiración.

* **RF-15: Mantenimiento y CRUD de catálogo y parámetros de costo por Administrador**
  * **Descripción:** El sistema debe permitir a un administrador crear, actualizar y desactivar motos y accesorios, así como configurar los parámetros financieros globales (precio del galón de gasolina, tarifas de SOAT e impuesto vehicular).
  * **Reglas asociadas:** RN-01.
  * **Entradas:** Token de administrador y datos del recurso a modificar (`Moto`, `Accesorio` o `ParametrosCosto`).
  * **Salida:** Registros persistidos y actualizados en la base de datos relacional.

* **RF-16: Generación analítica de Radar de Demanda con DuckDB**
  * **Descripción:** El sistema debe cruzar las búsquedas guardadas por cuota frente al inventario físico para generar un radar de demanda que identifique brechas de producto.
  * **Reglas asociadas:** N/A (Analítica).
  * **Entradas:** Token de administrador, rango de fechas y filtros de marca/cilindraje.
  * **Salida:** Reporte OLAP en DuckDB con volumen de búsquedas, marcas y rangos de cuota más demandados frente a las existencias.

* **RF-17: Generación de reporte analítico de ventas con DuckDB**
  * **Descripción:** El sistema debe calcular métricas de ventas de accesorios (ingresos brutos, ticket promedio, productos estrella y ventas por departamento) mediante consultas analíticas.
  * **Reglas asociadas:** N/A (Analítica).
  * **Entradas:** Token de administrador y periodo de consulta.
  * **Salida:** Reporte agregado de facturación y volumen de ventas generado mediante DuckDB.

---

## 2. Requisitos No Funcionales (RNF)

* **RNF-01 (Seguridad - Cifrado de Credenciales):** El sistema debe almacenar las contraseñas de los usuarios utilizando el algoritmo `bcrypt` con un factor de trabajo no menor a 12 rondas de salting, garantizando que ninguna credencial resida en texto plano.
  * *Regla asociada:* RN-12.

* **RNF-02 (Seguridad - Autenticación y Autorización RBAC):** El sistema debe proteger los endpoints mediante JSON Web Tokens (JWT) firmados con algoritmo HMAC-SHA256, expiración estricta (`JWT_EXPIRA_MINUTOS`) y restricción de acceso según el rol (`CLIENTE`, `ASESOR`, `ADMIN`).

* **RNF-03 (Seguridad - Mitigación BOLA / OWASP API1):** La API debe verificar la propiedad del recurso en rutas privadas (`/mis-...`, `/cotizaciones/{id}/estado`). Si el recurso no pertenece al usuario autenticado, el sistema debe responder `HTTP 404 Not Found` para evitar enumeración.
  * *Regla asociada:* RN-10.

* **RNF-04 (Seguridad - Integridad de Webhooks e Idempotencia por Evento):** El webhook de pagos debe recalcular el checksum SHA-256 usando el secreto de eventos (`WOMPI_SECRETO_EVENTOS`). Si no coincide, responderá `HTTP 401 Unauthorized`. Si el checksum del evento ya fue registrado previamente, retornará `HTTP 200 OK` sin reprocesar.
  * *Regla asociada:* RN-09.

* **RNF-05 (Disponibilidad y Resiliencia - Circuit Breaker):** La consulta externa de la TRM en datos.gov.co debe ejecutarse con cliente HTTP asíncrono y un patrón *Circuit Breaker* (Cerrado, Abierto, Semiabierto). Si el servicio falla reiteradamente, el circuito se abre y el sistema responde con el último valor conocido o degrada a mostrar solo precios en COP.

* **RNF-06 (Rendimiento - Latencia de Respuestas):** El backend debe resolver el 95% de las consultas de catálogo y costo real en menos de 300 ms bajo carga normal, empleando `asyncio.gather` para operaciones concurrentes independientes.

* **RNF-07 (Usabilidad y Accesibilidad - Principios Heurísticos de Nielsen):** La interfaz web debe aplicar consistencia visual basada en la identidad oficial de cada marca (Rojo Honda, Verde Kawasaki, Azul Yamaha) y ofrecer mensajes de retroalimentación claros ante validaciones de formularios.
  * *Regla asociada:* RN-01.

* **RNF-08 (Mantenibilidad - Arquitectura Hexagonal y DDD):** La capa de dominio (`domain`) no debe tener dependencias de frameworks ni de infraestructura. Las entidades y casos de uso solo interactúan con puertos abstractos (`abc.ABC`).

* **RNF-09 (Portabilidad - Aislamiento en Contenedores):** La aplicación debe ejecutarse de forma homogénea en Docker y `docker-compose`, desacoplando servicios de backend (FastAPI/Uvicorn), frontend (Angular/Nginx) y volumen de persistencia para SQLite.

* **RNF-10 (Calidad de Código y Pruebas Automatizadas):** El código debe cumplir con las reglas de estilo de `ruff` (límite de 100 caracteres por línea) y contar con suite de pruebas unitarias automatizadas con `pytest`.

---

## 3. Historias de Usuario (HU)

### HU-01: Búsqueda de motos según capacidad de pago mensual
* **Como:** Visitante del concesionario web.
* **Quiero:** Filtrar el catálogo de motos ingresando mi cuota mensual máxima y mi tipo de licencia.
* **Para:** Ver únicamente los modelos que puedo pagar y que puedo conducir legalmente.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-01, RN-02, RN-03.

**Criterios de Aceptación:**
* **Escenario 1: Filtrado exitoso para conductor con licencia A1**
  * **Dado** que un visitante ingresa una cuota mensual máxima de $350.000 COP, un plazo de 36 meses, cuota inicial de $1.000.000 COP y licencia "A1".
  * **Cuando** solicita la búsqueda de motocicletas.
  * **Entonces** el sistema calcula el precio máximo de adquisición con la fórmula de amortización fija y lista solo motos Honda, Kawasaki o Yamaha de cilindraje menor o igual a 125 cc cuyo precio encaje en el valor calculado.
* **Escenario 2: Restricción de modelos con licencia A1**
  * **Dado** que existen motos en catálogo de cilindraje superior a 125 cc que entran en el rango de cuota.
  * **Cuando** el usuario busca con licencia "A1".
  * **Entonces** el sistema excluye automáticamente dichas motos del listado.

---

### HU-02: Simulación de costo real mensual y modo trabajo
* **Como:** Visitante interesado en comprar una moto.
* **Quiero:** Calcular el costo total mensual proyectado seleccionando mi tipo de uso (ciudad, carretera o trabajo).
* **Para:** Conocer el gasto real de mantenimiento y saber en cuántos meses se paga la moto si trabajo en ella.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-03.

**Criterios de Aceptación:**
* **Escenario 1: Cálculo con uso estándar**
  * **Dado** que el usuario visualiza el detalle de una moto e ingresa 800 km/mes, plazo de 24 cuotas y selecciona perfil de uso "CIUDAD".
  * **Cuando** solicita calcular el costo real.
  * **Entonces** el sistema muestra el costo total mensual sumando cuota, combustible según el perfil, SOAT proporcional, impuesto y mantenimiento preventivo.
* **Escenario 2: Simulación en modo trabajo**
  * **Dado** que el usuario selecciona perfil de uso "TRABAJO" e ingresa ganancia diaria de $80.000 COP y 26 días de labor al mes.
  * **Cuando** ejecuta el cálculo.
  * **Entonces** el sistema resta el costo mensual de los ingresos proyectados y muestra la ganancia neta y el número estimado de meses para amortizar la moto.

---

### HU-03: Solicitud de cotización con asesor de marca
* **Como:** Visitante del catálogo.
* **Quiero:** Enviar una solicitud de cotización sin crear una cuenta.
* **Para:** Recibir asesoría de un especialista en la marca y tener un código para consultar el avance.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-01, RN-04, RN-05.

**Criterios de Aceptación:**
* **Escenario 1: Asignación balanceada de asesor**
  * **Dado** que hay dos asesores registrados para la marca de la moto, uno con 4 atenciones abiertas y otro con 2.
  * **Cuando** el visitante envía el formulario con sus datos de contacto y plan de pago.
  * **Entonces** el sistema asigna la cotización al asesor con 2 atenciones, genera un código único `CM-XXXX` y muestra en pantalla el nombre del asesor y el enlace a su WhatsApp.

---

### HU-04: Agendamiento de prueba de manejo (Test Drive)
* **Como:** Visitante interesado en probar una motocicleta.
* **Quiero:** Solicitar un test drive indicando mis datos de contacto, el modelo y mi fecha preferencial.
* **Para:** Agendar una prueba de manejo atendida por un asesor especialista.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-04, RN-05.

**Criterios de Aceptación:**
* **Escenario 1: Encolamiento de test drive**
  * **Dado** que un visitante completa el formulario con nombre, teléfono, correo, moto elegida y fecha preferencial.
  * **Cuando** envía la solicitud.
  * **Entonces** el sistema crea el registro en estado `PENDIENTE` dentro de la cola del asesor de la marca con menor carga y entrega al usuario un código `CM-XXXX`.

---

### HU-05: Consulta pública de seguimiento con código
* **Como:** Visitante que solicitó una cotización o test drive.
* **Quiero:** Digitar mi código alfanumérico en el módulo de seguimiento.
* **Para:** Verificar en qué estado se encuentra mi trámite sin iniciar sesión.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-05.

**Criterios de Aceptación:**
* **Escenario 1: Código válido**
  * **Dado** que el usuario ingresa un código existente `CM-1020`.
  * **Cuando** presiona consultar.
  * **Entonces** el sistema muestra el estado de la atención o del test drive, la fecha y la marca asociada.
* **Escenario 2: Código no registrado**
  * **Dado** que el usuario ingresa un código que no existe en el sistema.
  * **Cuando** presiona consultar.
  * **Entonces** el sistema responde un error HTTP 404 indicando que el registro no fue encontrado.

---

### HU-06: Gestión de atenciones y turnos en panel del asesor
* **Como:** Asesor comercial de una marca.
* **Quiero:** Consultar mis cotizaciones y atender el siguiente turno de mi cola de test drives.
* **Para:** Registrar el contacto con los clientes y gestionar mis pruebas de manejo en orden.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-04, RN-10.

**Criterios de Aceptación:**
* **Escenario 1: Visualización restringida a clientes propios**
  * **Dado** que un asesor ha iniciado sesión.
  * **Cuando** consulta sus cotizaciones.
  * **Entonces** el sistema lista únicamente las que le pertenecen y no las de otros asesores.
* **Escenario 2: Intento de modificar atención ajena**
  * **Dado** que un asesor intenta enviar un cambio de estado para una cotización de otro asesor.
  * **Cuando** el servidor procesa la petición.
  * **Entonces** el sistema retorna HTTP 404 (mitigando BOLA).

---

### HU-07: Registro e inicio de sesión de clientes
* **Como:** Comprador de accesorios.
* **Quiero:** Registrar una cuenta y autenticarme con mis credenciales.
* **Para:** Guardar mis direcciones de despacho y realizar compras seguras.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-10, RN-12.

**Criterios de Aceptación:**
* **Escenario 1: Registro seguro con hash bcrypt**
  * **Dado** que un nuevo cliente envía sus datos mediante `POST /auth/registro`.
  * **Cuando** se crea el usuario.
  * **Entonces** la contraseña se guarda cifrada con bcrypt y la respuesta no incluye el hash de la contraseña.
* **Escenario 2: Login con entrega de JWT**
  * **Dado** que un usuario ingresa sus credenciales correctas en `POST /auth/login`.
  * **Cuando** el backend valida las credenciales.
  * **Entonces** retorna un token JWT que contiene el ID de usuario, rol `CLIENTE` y tiempo de expiración.

---

### HU-08: Creación de pedido con dirección guardada y reserva de stock
* **Como:** Cliente registrado autenticado.
* **Quiero:** Crear un pedido eligiendo una de mis direcciones guardadas y reservar el stock.
* **Para:** Garantizar la disponibilidad de los accesorios durante el proceso de pago virtual.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-06, RN-07, RN-10, RN-11.

**Criterios de Aceptación:**
* **Escenario 1: Creación con precio de backend y reserva**
  * **Dado** que un cliente autenticado tiene accesorios en su carrito y selecciona una `direccion_id` guardada.
  * **Cuando** envía `POST /pedidos`.
  * **Entonces** el backend calcula el total con precios de la base de datos, agrega el flete del departamento de la dirección, descuenta el stock reservándolo por 15 minutos en estado `PENDIENTE_PAGO` y entrega los datos para abrir el widget de Wompi.

---

### HU-09: Confirmación de pago e idempotencia por checksum de evento
* **Como:** Sistema Candela Motors.
* **Quiero:** Recibir el aviso de pago de Wompi, validar la firma y verificar el checksum del evento.
* **Para:** Aprobar el pedido y generar el envío sin duplicar órdenes ante múltiples avisos de una transacción.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-08, RN-09.

**Criterios de Aceptación:**
* **Escenario 1: Aviso de pago aprobado y creación de envío**
  * **Dado** que llega un webhook de Wompi con estado `APPROVED` y firma válida.
  * **Cuando** el checksum del evento no ha sido registrado previamente.
  * **Entonces** el pedido cambia a `PAGADO`, se guarda el evento y se genera la orden de envío en estado `PREPARANDO`.
* **Escenario 2: Aviso repetido del mismo evento**
  * **Dado** que llega un aviso con un checksum de evento que ya fue procesado con anterioridad.
  * **Cuando** el webhook lo detecta.
  * **Entonces** responde `HTTP 200 OK` inmediatamente sin alterar el inventario ni duplicar registros de envío.

---

### HU-10: Seguimiento del pedido y línea de tiempo de despacho
* **Como:** Cliente que compró accesorios.
* **Quiero:** Entrar a mis pedidos y ver el avance del envío en tiempo real.
* **Para:** Conocer la fecha y estado de despacho de mis productos.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-10.

**Criterios de Aceptación:**
* **Escenario 1: Consulta de pedido propio**
  * **Dado** que un cliente consulta uno de sus pedidos en `GET /mis-pedidos/{id}`.
  * **Cuando** se valida su pertenencia.
  * **Entonces** observa la línea de tiempo (`PREPARANDO` → `ENVIADO` → `EN_CAMINO` → `ENTREGADO`) con sus marcas de fecha.
* **Escenario 2: Intento de ver pedido ajeno**
  * **Dado** que un cliente intenta consultar el ID de un pedido que pertenece a otro usuario.
  * **Cuando** el servidor valida el token.
  * **Entonces** responde `HTTP 404 Not Found`.

---

### HU-11: Gestión administrativa del ciclo de envíos
* **Como:** Administrador del sistema.
* **Quiero:** Consultar todos los pedidos pagados y actualizar el estado de sus envíos.
* **Para:** Mantener el seguimiento logístico al día conforme avanzan los paquetes.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-08.

**Criterios de Aceptación:**
* **Escenario 1: Avance secuencial de envío**
  * **Dado** que un envío está en estado `PREPARANDO`.
  * **Cuando** el administrador envía `PATCH /envios/{id}/estado` con valor `ENVIADO`.
  * **Entonces** el estado cambia a `ENVIADO` y se registra el evento en la cronología.
* **Escenario 2: Intento de transición inválida**
  * **Dado** que un envío ya se encuentra en `ENTREGADO`.
  * **Cuando** se intenta cambiar a `PREPARANDO`.
  * **Entonces** la API retorna error `HTTP 409 Conflict`.

---

### HU-12: Mantenimiento de catálogo y parámetros de costo
* **Como:** Administrador de Candela Motors.
* **Quiero:** Gestionar las motos, accesorios y los valores del galón de gasolina, SOAT e impuesto vehicular.
* **Para:** Mantener actualizados los precios y la exactitud en las fórmulas de costo real.
* **Prioridad:** Obligatorio.
* **Reglas de Negocio:** RN-01.

**Criterios de Aceptación:**
* **Escenario 1: Actualización de parámetros de costo**
  * **Dado** que el administrador envía nuevos valores en `PUT /parametros-costo`.
  * **Cuando** la petición es autenticada con rol `ADMIN`.
  * **Entonces** los valores de combustible, SOAT e impuesto quedan actualizados para todos los cálculos subsiguientes.
* **Escenario 2: Restricción de marcas en motos**
  * **Dado** que el administrador intenta crear una moto con una marca distinta a Honda, Kawasaki o Yamaha.
  * **Cuando** la petición llega al dominio.
  * **Entonces** se rechaza la creación cumpliendo con la regla RN-01.

---

### HU-13: Análisis de Radar de Demanda frente a Inventario
* **Como:** Administrador del concesionario.
* **Quiero:** Consultar el reporte analítico de búsquedas de motos versus el inventario disponible.
* **Para:** Conocer qué cilindrajes y marcas buscan más los clientes y ajustar compras de stock.
* **Prioridad:** Ligero.
* **Reglas de Negocio:** N/A (Analítica).

**Criterios de Aceptación:**
* **Escenario 1: Generación de reporte OLAP**
  * **Dado** que el administrador solicita `GET /reportes/demanda`.
  * **Cuando** el backend ejecuta la agregación en DuckDB sobre la tabla de búsquedas guardadas.
  * **Entonces** retorna los modelos y marcas más cotizados frente al volumen de unidades físicas disponibles en tienda.

---

## 4. Matriz de Trazabilidad: Reglas de Negocio vs. Requisitos e Historias

| Regla de Negocio | Descripción General | Requisitos Funcionales | Requisitos No Funcionales | Historias de Usuario |
| :--- | :--- | :--- | :--- | :--- |
| **RN-01** | Solo marcas Honda, Kawasaki y Yamaha | RF-01, RF-03, RF-04, RF-15 | RNF-07 | HU-01, HU-03, HU-12 |
| **RN-02** | Clasificación A1 (≤125 cc) y A2 (>125 cc) | RF-01 | — | HU-01 |
| **RN-03** | Amortización fija para cálculo de cuota | RF-01, RF-02 | — | HU-01, HU-02 |
| **RN-04** | Asignación de asesor con menor carga | RF-04, RF-05, RF-07 | — | HU-03, HU-04, HU-06 |
| **RN-05** | Código único de seguimiento `CM-XXXX` | RF-04, RF-05, RF-06 | — | HU-03, HU-04, HU-05 |
| **RN-06** | Total calculado exclusivamente en backend | RF-10 | — | HU-08 |
| **RN-07** | Reserva de stock por 15 minutos | RF-10, RF-12 | — | HU-08 |
| **RN-08** | Envío se crea tras pago aprobado | RF-11, RF-13 | — | HU-09, HU-11 |
| **RN-09** | Firma SHA-256 e idempotencia por checksum de evento | RF-11 | RNF-04 | HU-09 |
| **RN-10** | Aislamiento de datos del cliente (BOLA) | RF-07, RF-09, RF-10, RF-14 | RNF-03 | HU-06, HU-07, HU-08, HU-10 |
| **RN-11** | Tarifa de envío por departamento | RF-09, RF-10 | — | HU-08 |
| **RN-12** | Contraseñas con hashing bcrypt | RF-14 | RNF-01 | HU-07 |
