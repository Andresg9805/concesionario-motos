# Normalización de la base de datos

Cuando revisamos el primer modelo de la base de datos encontramos datos repetidos y columnas que se podían calcular. Este documento explica qué estaba mal, cómo lo corregimos y con qué forma normal tiene que ver cada cambio. El resultado final está en `docs/uml/modelo-logico-relacional.png` y `docs/uml/modelo-entidad-relacion.png`.

## Repaso rápido

- **1FN:** cada columna guarda un solo dato (nada de listas ni datos mezclados en un texto) y cada fila se puede identificar con una llave.
- **2FN:** está en 1FN y ninguna columna depende solo de una parte de la llave. Esto solo pasa en tablas con llave compuesta.
- **3FN:** está en 2FN y ninguna columna depende de otra columna que no sea la llave (no hay dependencias transitivas). En la práctica: no guardar lo que se puede calcular a partir de otras columnas.

## Lo que encontramos y cómo quedó

### 1. Los datos de una persona estaban dos veces (redundancia)

Antes `usuarios` y `clientes` tenían las dos `nombre`, `correo` y `telefono`. Si un cliente cotizaba y después creaba su cuenta, sus datos quedaban guardados dos veces y podían quedar distintos (por ejemplo, cambia el teléfono en una tabla y en la otra no).

**Cómo quedó:**

| Tabla | Columnas |
| --- | --- |
| `personas` | id, nombre, correo (único), telefono |
| `usuarios` | id, persona_id (único), hash_contrasena, rol |
| `asesores` | usuario_id, marca_id |

Ahora el nombre, el correo y el teléfono están en un solo lugar. Las cotizaciones y los test drives apuntan a `personas`, y si esa persona después crea su cuenta se usa la misma fila (hay una prueba que lo revisa).

También sacamos `marca_especialidad_id` de `usuarios`. Esa columna solo tenía sentido para los asesores y en los clientes y el administrador siempre quedaba vacía. Ahora está en la tabla `asesores`, y las cotizaciones y test drives apuntan a `asesores`, así la base de datos no deja asignar una cotización a alguien que no es asesor.

### 2. Columnas que se podían calcular (3FN)

| Columna que quitamos | De qué dependía |
| --- | --- |
| `motos.categoria_licencia` | Del cilindraje: hasta 125 cc es A1, más es A2. Dependía de `cilindraje_cc` y no de la llave. |
| `cotizaciones.cuota_mensual_cop` | Del precio, la cuota inicial, el plazo y la tasa, que ya están en la misma fila. |
| `pedidos.subtotal_cop` | De la suma de `cantidad × precio_unitario_cop` de sus ítems. |
| `pedidos.total_cop` | Del subtotal más el costo de envío. |
| `envios.costo_cop` | Repetía `pedidos.costo_envio_cop`. |
| `envios.estado` | Repetía el último registro de `eventos_envio`. |

Estos valores se siguen mostrando en la página y en la API, pero ahora los calcula el dominio. Así no puede pasar que, por ejemplo, una moto de 184 cc quede marcada como A1 por un error al digitar.

**Lo que sí dejamos a propósito:** `cotizaciones.precio_cop`, `cotizaciones.tasa_mensual`, `items_pedido.precio_unitario_cop` y `pedidos.costo_envio_cop` se parecen a datos de otras tablas, pero no son repetidos: son la "foto" del valor el día de la cotización o de la compra. Si mañana sube el precio de la moto, la cotización vieja no debe cambiar. Como dependen de la cotización o del pedido (que es su llave), no rompen la 3FN.

### 3. Catálogos guardados como texto suelto

- El tipo de moto era un `ENUM` en `motos`. Ahora es la tabla `tipos_moto` (Naked, Doble propósito, Trail, Deportiva) y `motos` tiene `tipo_id`. Así el nombre que se muestra ("Doble propósito") se escribe una sola vez.
- La categoría del accesorio era un `ENUM`. Ahora es la tabla `categorias_accesorio` y `accesorios` tiene `categoria_id`.
- La marca del accesorio estaba metida dentro del nombre ("SHOEI X-Fifteen", "Protectores De Rodillas Nucleon Flex Pro alpinestars"), escrita de distintas formas y sin forma de filtrar por ella. Eso rompe la 1FN porque una sola columna guardaba dos datos. Ahora es la tabla `fabricantes` (SHOEI, Alpinestars, GIVI, SAS-TEC, Honda, Kawasaki, Yamaha) y el nombre del producto quedó limpio ("X-Fifteen").

Los estados (de la cotización, del test drive, del pedido, del pago y del envío) los dejamos como `ENUM` porque no son datos que el administrador cambie: son los pasos fijos de cada proceso y el dominio controla cómo se pasa de uno a otro.

### 4. Faltaban restricciones de único

- `marcas.nombre` no era único, así que se podía registrar "Honda" dos veces. Ahora es único.
- Nada impedía cargar la misma moto dos veces. Ahora `motos` tiene la restricción única `(marca_id, modelo, anio)`.

### 5. Una tabla que ya no corresponde

`compatibilidades` relacionaba accesorios con motos, pero los accesorios de la tienda son para el motociclista (casco, chaqueta, guantes…) y no para un modelo de moto. Se eliminó la tabla y también el filtro `moto_id` de `GET /accesorios`.

### 6. Un error de diseño

`test_drives.fecha_programada` era obligatoria, pero un test drive recién pedido todavía no tiene fecha. Ahora puede quedar vacía mientras el test drive está pendiente.

### 7. Columnas que faltaban

Al conectar la API a SQLite vimos que dos tablas no guardaban datos que el dominio sí usa:

| Tabla | Columna nueva | Por qué no rompe la 3FN |
| --- | --- | --- |
| `parametros_costo` | `valor_matricula_cop`, `valor_tramites_cop`, `tasa_mensual` | Son parámetros que configura el administrador, igual que el precio del galón. No se calculan a partir de otra columna |
| `busquedas` | `categoria_licencia` | Es la licencia que escogió la persona al buscar (A1 o A2). No sale de ninguna otra columna de la búsqueda |

Sin estas columnas, el costo real con SQLite salía sin matrícula ni trámites, y el radar de demanda no podía separar las búsquedas por licencia.

## Otros ajustes

- Los datos de prueba de la API en memoria y los datos que se cargan en la base de datos salen de los mismos archivos (`app/infrastructure/db/seeds`). Antes había dos versiones de las marcas con colores y descripciones distintas.
- Los repositorios con SQLAlchemy convierten de tablas a clases del dominio desde un solo archivo (`repositorios/conversiones.py`). Antes ese código estaba copiado en tres repositorios.

## Cómo lo comprobamos

En `backend/tests/bd/test_normalizacion.py` hay pruebas que revisan que:

- la carga inicial deja 3 marcas, 60 motos (15 por tipo) y 35 accesorios, y que cargar dos veces no duplica nada;
- no se pueden repetir marcas, motos ni correos;
- la licencia se calcula con el cilindraje;
- un cliente que después crea su cuenta sigue siendo una sola persona;
- ninguna de las columnas que quitamos volvió a aparecer.
