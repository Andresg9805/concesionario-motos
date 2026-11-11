# Diagrama de clases del dominio: Candela Motors

Este diagrama muestra las clases de la capa de dominio (`backend/app/domain/`). Está dividido en nueve partes para que se pueda leer bien. Las fuentes en Mermaid están en `docs/uml/fuentes/`; si algo cambia, se edita la fuente y se vuelve a exportar la imagen.

El alcance completo está en [docs/alcance.md](../alcance.md).

## 1. Catálogo de motos

Las motos son de tres marcas fijas (Honda, Kawasaki y Yamaha), y cada `Marca` guarda su color para pintar la página. `Moto` sabe si está disponible, si sirve para una licencia (A1 hasta 125 cc, A2 más de 125 cc) y cuánto vale en dólares con la TRM. `PlanCredito` es un value object: calcula la cuota con la fórmula de cuota fija y, al revés, el precio máximo que alcanza para una cuota (`precio_maximo_para_cuota`), que es la base de "buscar por cuota". Cada búsqueda se guarda sin datos personales en `Busqueda` para el radar de demanda.

![Catálogo de motos](diagrama-clases-01-catalogo.png)

```mermaid
classDiagram
    direction TB

    class Marca {
        +id: int
        +nombre: str
        +color_hex: str
        +descripcion: str
    }

    class Moto {
        +id: int
        +marca: Marca
        +modelo: str
        +anio: int
        +cilindraje_cc: int
        +tipo: TipoMoto
        +categoria_licencia: CategoriaLicencia
        +precio_cop: int
        +stock: int
        +consumo_km_galon: float
        +costo_mantenimiento_km_cop: int
        +descripcion: str
        +imagen_url: str
        +esta_disponible() bool
        +apta_para(licencia: CategoriaLicencia) bool
        +precio_en_usd(trm: TasaCambio) float
        +categoria_por_cilindraje(cilindraje_cc: int)$ CategoriaLicencia
    }

    class TipoMoto {
        <<enumeration>>
        NAKED
        DOBLE_PROPOSITO
        DEPORTIVA
        TRAIL
    }

    class CategoriaLicencia {
        <<enumeration>>
        A1
        A2
    }

    class TasaCambio {
        <<value object>>
        +valor: float
        +fecha: date
    }

    class PlanCredito {
        <<value object>>
        +precio_cop: int
        +cuota_inicial_cop: int
        +plazo_meses: int
        +tasa_mensual: float
        +monto_financiado() int
        +cuota_mensual() int
        +precio_maximo_para_cuota(cuota: int, cuota_inicial: int, plazo: int, tasa: float)$ int
    }

    class Busqueda {
        +id: int
        +fecha: datetime
        +cuota_maxima_cop: int
        +cuota_inicial_cop: int
        +categoria_licencia: CategoriaLicencia
        +uso: UsoMoto
        +marca_id: int
        +cantidad_resultados: int
    }

    Moto "*" --> "1" Marca : pertenece a
    Moto --> TipoMoto
    Moto --> CategoriaLicencia
    Moto ..> TasaCambio : usa
    PlanCredito ..> Moto : precio de
```

## 2. Costo real de tener la moto

`CalculadoraCostoReal` es un servicio de dominio. Junta la moto, el plan de crédito, el perfil de uso y los parámetros que configura el administrador, y devuelve un `CostoMensual` con el desglose: cuota, gasolina, SOAT, mantenimiento e impuesto. El costo de mantenimiento por kilómetro está en cada moto, y el SOAT sale de la tabla `TarifaSoat` según el cilindraje. Con el perfil de uso también calcula en cuántos meses se paga la moto cuando se usa para trabajar.

![Costo real de tener la moto](diagrama-clases-02-costo-real.png)

```mermaid
classDiagram
    direction LR

    class CalculadoraCostoReal {
        <<service>>
        +calcular(moto: Moto, plan: PlanCredito, perfil: PerfilUso, parametros: ParametrosCosto) CostoMensual
        +meses_para_pagarse(costo: CostoMensual, perfil: PerfilUso, plan: PlanCredito) int
    }

    class PerfilUso {
        <<value object>>
        +km_mes: int
        +uso: UsoMoto
        +ganancia_diaria_cop: int
        +dias_trabajo_mes: int
        +ganancia_mensual() int
    }

    class UsoMoto {
        <<enumeration>>
        CIUDAD
        CARRETERA
        TRABAJO
    }

    class CostoMensual {
        <<value object>>
        +cuota_credito_cop: int
        +gasolina_cop: int
        +soat_cop: int
        +mantenimiento_cop: int
        +impuesto_cop: int
        +total() int
    }

    class ParametrosCosto {
        +precio_galon_cop: int
        +porcentaje_impuesto: float
        +tarifas_soat: list~TarifaSoat~
        +soat_mensual(cilindraje_cc: int) int
        +impuesto_mensual(precio_cop: int, cilindraje_cc: int) int
    }

    class TarifaSoat {
        <<value object>>
        +cilindraje_min: int
        +cilindraje_max: int
        +valor_anual_cop: int
        +aplica(cilindraje_cc: int) bool
    }

    class Moto
    class PlanCredito

    CalculadoraCostoReal ..> Moto : usa
    CalculadoraCostoReal ..> PlanCredito : usa
    CalculadoraCostoReal ..> PerfilUso : usa
    CalculadoraCostoReal ..> ParametrosCosto : usa
    CalculadoraCostoReal ..> CostoMensual : crea
    PerfilUso --> UsoMoto
    ParametrosCosto *-- "*" TarifaSoat
```

## 3. Atención personalizada

Un `Cliente` es la persona que cotiza o pide un test drive; puede tener una cuenta (`Usuario` con rol `CLIENTE`) o no. Los asesores también son usuarios, con rol `ASESOR` y una marca de especialidad. `AsignadorAsesor` elige al asesor de la marca con menos atenciones abiertas, y `GeneradorCodigo` crea el código de seguimiento (`CM-XXXX`). La `Cotizacion` avanza por los estados de `EstadoAtencion` con `cambiar_estado`, que no deja hacer saltos inválidos.

![Atención personalizada](diagrama-clases-03-atencion.png)

```mermaid
classDiagram
    direction TB

    class Usuario {
        +id: int
        +nombre: str
        +correo: str
        +telefono: str
        +hash_contrasena: str
        +rol: Rol
        +marca_especialidad: Marca
        +es_admin() bool
        +es_asesor() bool
        +enlace_whatsapp() str
    }

    class Rol {
        <<enumeration>>
        CLIENTE
        ASESOR
        ADMIN
    }

    class Cliente {
        +id: int
        +nombre: str
        +correo: str
        +telefono: str
        +usuario: Usuario
    }

    class Cotizacion {
        +id: int
        +codigo_seguimiento: str
        +cliente: Cliente
        +moto: Moto
        +asesor: Usuario
        +fecha: date
        +plan: PlanCredito
        +estado: EstadoAtencion
        +cuota_mensual() int
        +cambiar_estado(nuevo: EstadoAtencion) None
        +esta_abierta() bool
    }

    class EstadoAtencion {
        <<enumeration>>
        NUEVO
        CONTACTADO
        TEST_DRIVE
        NEGOCIANDO
        VENDIDO
        DESCARTADO
    }

    class TestDrive {
        +id: int
        +codigo_seguimiento: str
        +cliente: Cliente
        +moto: Moto
        +asesor: Usuario
        +fecha_solicitud: datetime
        +fecha_programada: datetime
        +estado: EstadoTestDrive
        +programar(fecha: datetime) None
        +marcar_realizado() None
        +cancelar() None
    }

    class EstadoTestDrive {
        <<enumeration>>
        PENDIENTE
        PROGRAMADO
        REALIZADO
        CANCELADO
    }

    class AsignadorAsesor {
        <<service>>
        +elegir(asesores: list~Usuario~, abiertas_por_asesor: dict) Usuario
    }

    class GeneradorCodigo {
        <<service>>
        +nuevo_codigo()$ str
    }

    class Moto
    class Marca
    class PlanCredito

    GeneradorCodigo ..> Cotizacion : codigo
    EstadoAtencion <-- Cotizacion
    EstadoTestDrive <-- TestDrive
    Cotizacion *-- "1" PlanCredito
    Cotizacion "*" --> "1" Cliente : la pide
    TestDrive "*" --> "1" Cliente : lo pide
    Cotizacion "*" --> "1" Moto : de
    TestDrive "*" --> "1" Moto : de
    Cotizacion "*" --> "1" Usuario : asesor
    TestDrive "*" --> "1" Usuario : asesor
    Cliente "0..1" --> "0..1" Usuario : cuenta
    AsignadorAsesor ..> Usuario : elige
    Usuario "*" --> "0..1" Marca : especialista en
    Usuario --> Rol
```

## 4. Tienda de accesorios

Un `Accesorio` puede servir para muchas motos y una moto acepta muchos accesorios (relación muchos a muchos). El `Pedido` se compone de `ItemPedido`, y cada ítem guarda el precio del día en que se compró. El pedido sabe si su reserva de stock ya venció (`reserva_vencida`). La `Direccion` usa los municipios y departamentos oficiales, y el departamento define el costo y los días de envío.

![Tienda de accesorios](diagrama-clases-04-tienda.png)

```mermaid
classDiagram
    direction TB

    class Accesorio {
        +id: int
        +sku: str
        +nombre: str
        +categoria: CategoriaAccesorio
        +descripcion: str
        +precio_cop: int
        +stock: int
        +imagen_url: str
        +motos_compatibles: list~Moto~
        +hay_stock(cantidad: int) bool
        +reservar(cantidad: int) None
        +liberar(cantidad: int) None
    }

    class CategoriaAccesorio {
        <<enumeration>>
        CASCO
        CHAQUETA
        GUANTES
        MALETA
        MANTENIMIENTO
    }

    class Pedido {
        +id: int
        +usuario: Usuario
        +direccion: Direccion
        +items: list~ItemPedido~
        +estado: EstadoPedido
        +subtotal_cop: int
        +costo_envio_cop: int
        +creado_en: datetime
        +reservado_hasta: datetime
        +total_cop() int
        +reserva_vencida(ahora: datetime) bool
        +marcar_pagado() None
        +expirar() None
    }

    class ItemPedido {
        +accesorio: Accesorio
        +cantidad: int
        +precio_unitario_cop: int
        +subtotal() int
    }

    class EstadoPedido {
        <<enumeration>>
        PENDIENTE_PAGO
        PAGADO
        EXPIRADO
    }

    class Direccion {
        +id: int
        +usuario: Usuario
        +municipio: Municipio
        +detalle: str
        +telefono_contacto: str
    }

    class Municipio {
        +codigo: str
        +nombre: str
        +departamento: Departamento
    }

    class Departamento {
        +codigo: str
        +nombre: str
        +costo_envio_cop: int
        +dias_envio: int
    }

    class Moto
    class Usuario

    Accesorio --> CategoriaAccesorio
    Accesorio "*" -- "*" Moto : compatible con
    Pedido *-- "1..*" ItemPedido
    ItemPedido "*" --> "1" Accesorio
    Pedido --> EstadoPedido
    Pedido "*" --> "1" Usuario : lo hace
    Pedido "*" --> "1" Direccion : se envia a
    Direccion "*" --> "1" Usuario
    Direccion "*" --> "1" Municipio
    Municipio "*" --> "1" Departamento
```

## 5. Pagos y envíos

Un pedido puede tener varios intentos de `Pago` (si el primero es rechazado). `ResultadoPago` es lo que responde la pasarela (Wompi): con él se aprueba o se rechaza el pago. Cuando el pago queda aprobado se crea el `Envio`, que guarda cada cambio de estado como un `EventoEnvio`; así el cliente ve la línea de tiempo de su pedido.

![Pagos y envíos](diagrama-clases-05-pagos-envios.png)

```mermaid
classDiagram
    direction TB

    class Pedido

    class Pago {
        +id: int
        +pedido: Pedido
        +referencia: str
        +transaccion_id: str
        +metodo: MetodoPago
        +estado: EstadoPago
        +monto_cop: int
        +monto_en_centavos() int
        +aprobar(transaccion_id: str) None
        +rechazar() None
    }

    class MetodoPago {
        <<enumeration>>
        TARJETA
        NEQUI
        PSE
    }

    class EstadoPago {
        <<enumeration>>
        PENDIENTE
        APROBADO
        RECHAZADO
        ERROR
    }

    class ResultadoPago {
        <<value object>>
        +referencia: str
        +transaccion_id: str
        +estado: EstadoPago
        +monto_cop: int
    }

    class Envio {
        +id: int
        +pedido: Pedido
        +numero_guia: str
        +costo_cop: int
        +estado: EstadoEnvio
        +eventos: list~EventoEnvio~
        +avanzar(nuevo: EstadoEnvio, nota: str) None
    }

    class EstadoEnvio {
        <<enumeration>>
        PREPARANDO
        ENVIADO
        EN_CAMINO
        ENTREGADO
    }

    class EventoEnvio {
        +estado: EstadoEnvio
        +fecha: datetime
        +nota: str
    }

    Pedido "1" <-- "*" Pago : intento de pago
    Pago --> MetodoPago
    Pago --> EstadoPago
    ResultadoPago --> EstadoPago
    Pago ..> ResultadoPago : se actualiza con
    Pedido "1" <-- "0..1" Envio : despacha
    Envio --> EstadoEnvio
    Envio *-- "*" EventoEnvio
```

## 6. Puertos: motos y atención

Los puertos son interfaces (clases abstractas con `abc.ABC`) que el dominio define y la infraestructura implementa. Laura implementa los repositorios con SQLAlchemy y Nicolás implementa `ProveedorTasaCambio` con la API de la TRM. `contar_abiertas_por_asesor` le da al `AsignadorAsesor` los datos para elegir asesor.

![Puertos: motos y atención](diagrama-clases-06-puertos-motos-atencion.png)

```mermaid
classDiagram
    direction LR

    class RepositorioMotos {
        <<interface>>
        +listar(filtros: FiltrosMoto) list~Moto~
        +buscar_por_id(id: int) Moto
        +guardar(moto: Moto) Moto
        +eliminar(id: int) None
    }

    class RepositorioMarcas {
        <<interface>>
        +listar() list~Marca~
        +buscar_por_id(id: int) Marca
    }

    class RepositorioParametros {
        <<interface>>
        +obtener() ParametrosCosto
        +guardar(parametros: ParametrosCosto) ParametrosCosto
    }

    class RepositorioBusquedas {
        <<interface>>
        +guardar(busqueda: Busqueda) Busqueda
    }

    class RepositorioClientes {
        <<interface>>
        +guardar(cliente: Cliente) Cliente
        +buscar_por_correo(correo: str) Cliente
    }

    class RepositorioUsuarios {
        <<interface>>
        +guardar(usuario: Usuario) Usuario
        +buscar_por_correo(correo: str) Usuario
        +listar_asesores(marca_id: int) list~Usuario~
    }

    class RepositorioCotizaciones {
        <<interface>>
        +guardar(cotizacion: Cotizacion) Cotizacion
        +buscar_por_codigo(codigo: str) Cotizacion
        +listar_por_asesor(asesor_id: int) list~Cotizacion~
        +listar_por_usuario(usuario_id: int) list~Cotizacion~
        +contar_abiertas_por_asesor(marca_id: int) dict
    }

    class RepositorioTestDrives {
        <<interface>>
        +guardar(test_drive: TestDrive) TestDrive
        +buscar_por_codigo(codigo: str) TestDrive
        +listar_pendientes(asesor_id: int) list~TestDrive~
    }

    class ProveedorTasaCambio {
        <<interface>>
        +obtener_trm() TasaCambio
    }

    class FiltrosMoto {
        <<value object>>
        +marca_id: int
        +tipo: TipoMoto
        +categoria_licencia: CategoriaLicencia
        +precio_min: int
        +precio_max: int
    }

    class Moto
    class Marca
    class ParametrosCosto
    class Busqueda
    class Cliente
    class Usuario
    class Cotizacion
    class TestDrive
    class TasaCambio

    RepositorioMotos ..> Moto
    RepositorioMotos ..> FiltrosMoto
    RepositorioMarcas ..> Marca
    RepositorioParametros ..> ParametrosCosto
    RepositorioBusquedas ..> Busqueda
    RepositorioClientes ..> Cliente
    RepositorioUsuarios ..> Usuario
    RepositorioCotizaciones ..> Cotizacion
    RepositorioTestDrives ..> TestDrive
    ProveedorTasaCambio ..> TasaCambio
```

## 7. Puertos: tienda, pagos y envíos

`RepositorioPedidos.crear_con_reserva` guarda el pedido, sus ítems y descuenta el stock en una sola transacción: si algo falla, no queda nada a medias. `RepositorioPagos.registrar_evento` devuelve `False` si ese aviso de Wompi ya había llegado, para no procesarlo dos veces. `PasarelaPago` es el puerto que Nicolás implementa con Wompi: arma los datos del widget, lee el aviso (validando la firma) y consulta una transacción.

![Puertos: tienda, pagos y envíos](diagrama-clases-07-puertos-tienda.png)

```mermaid
classDiagram
    direction LR

    class RepositorioAccesorios {
        <<interface>>
        +listar(categoria: CategoriaAccesorio, moto_id: int) list~Accesorio~
        +buscar_por_id(id: int) Accesorio
        +guardar(accesorio: Accesorio) Accesorio
        +eliminar(id: int) None
    }

    class RepositorioUbicaciones {
        <<interface>>
        +listar_departamentos() list~Departamento~
        +listar_municipios(departamento_codigo: str) list~Municipio~
        +buscar_municipio(codigo: str) Municipio
    }

    class RepositorioDirecciones {
        <<interface>>
        +guardar(direccion: Direccion) Direccion
        +buscar_por_id(id: int) Direccion
        +listar_por_usuario(usuario_id: int) list~Direccion~
    }

    class RepositorioPedidos {
        <<interface>>
        +crear_con_reserva(pedido: Pedido) Pedido
        +buscar_por_id(id: int) Pedido
        +guardar(pedido: Pedido) Pedido
        +listar_por_usuario(usuario_id: int) list~Pedido~
        +listar_vencidos(ahora: datetime) list~Pedido~
    }

    class RepositorioPagos {
        <<interface>>
        +guardar(pago: Pago) Pago
        +buscar_por_referencia(referencia: str) Pago
        +registrar_evento(pago_id: int, checksum: str) bool
    }

    class RepositorioEnvios {
        <<interface>>
        +guardar(envio: Envio) Envio
        +buscar_por_pedido(pedido_id: int) Envio
        +listar() list~Envio~
    }

    class PasarelaPago {
        <<interface>>
        +datos_para_widget(pago: Pago) dict
        +leer_evento(cuerpo: dict) ResultadoPago
        +consultar_transaccion(transaccion_id: str) ResultadoPago
    }

    class Accesorio
    class Departamento
    class Municipio
    class Direccion
    class Pedido
    class Pago
    class Envio
    class ResultadoPago

    RepositorioAccesorios ..> Accesorio
    RepositorioUbicaciones ..> Departamento
    RepositorioUbicaciones ..> Municipio
    RepositorioDirecciones ..> Direccion
    RepositorioPedidos ..> Pedido
    RepositorioPagos ..> Pago
    RepositorioEnvios ..> Envio
    PasarelaPago ..> ResultadoPago
```

## 8. Excepciones

Todas las excepciones del dominio heredan de `DominioError`. La API las convierte en respuestas HTTP: `EntidadNoEncontradaError` en 404, `StockInsuficienteError` y `TransicionInvalidaError` en 409, `FirmaInvalidaError` en 401, y las demás de validación en 422.

![Excepciones](diagrama-clases-08-excepciones.png)

```mermaid
classDiagram
    direction LR

    class DominioError {
        <<exception>>
        +mensaje: str
    }

    class EntidadNoEncontradaError {
        <<exception>>
    }
    class MotoNoDisponibleError {
        <<exception>>
    }
    class CreditoInvalidoError {
        <<exception>>
    }
    class TestDriveInvalidoError {
        <<exception>>
    }
    class SinAsesorDisponibleError {
        <<exception>>
    }
    class TransicionInvalidaError {
        <<exception>>
    }
    class StockInsuficienteError {
        <<exception>>
    }
    class PedidoInvalidoError {
        <<exception>>
    }
    class ReservaVencidaError {
        <<exception>>
    }
    class PagoInvalidoError {
        <<exception>>
    }
    class FirmaInvalidaError {
        <<exception>>
    }

    DominioError <|-- EntidadNoEncontradaError
    DominioError <|-- MotoNoDisponibleError
    DominioError <|-- CreditoInvalidoError
    DominioError <|-- TestDriveInvalidoError
    DominioError <|-- SinAsesorDisponibleError
    DominioError <|-- TransicionInvalidaError
    DominioError <|-- StockInsuficienteError
    DominioError <|-- PedidoInvalidoError
    DominioError <|-- ReservaVencidaError
    DominioError <|-- PagoInvalidoError
    DominioError <|-- FirmaInvalidaError
```

## 9. Estructuras de datos

| Estructura | Para qué se usa | Complejidad |
| --- | --- | --- |
| ColaTestDrives | Atender los test drives de un asesor en el orden en que se pidieron (FIFO) | encolar y desencolar O(1) |
| AgendaTestDrives | Guardar una cola por asesor y atender al siguiente de cada uno | encontrar la cola del asesor O(1) en promedio |
| PilaSimulaciones | Deshacer la última simulación en el simulador de crédito | apilar y desapilar O(1) |
| ArbolMotosPorPrecio | Encontrar las motos que alcanzan con la cuota del cliente (árbol binario de búsqueda por precio) | insertar y buscar O(log n) en promedio, O(n) en el peor caso; buscar un rango O(log n + k) |

La cola y la pila están hechas con nodos enlazados, sin usar `list.pop(0)` ni `collections.deque`.

![Estructuras de datos](diagrama-clases-09-estructuras.png)

```mermaid
classDiagram
    direction LR

    class Nodo~T~ {
        +valor: T
        +siguiente: Nodo
    }

    class ColaTestDrives {
        -frente: Nodo
        -final: Nodo
        -cantidad: int
        +encolar(test_drive: TestDrive) None
        +desencolar() TestDrive
        +ver_frente() TestDrive
        +esta_vacia() bool
        +tamano() int
    }

    class AgendaTestDrives {
        -colas: dict
        +encolar(asesor_id: int, test_drive: TestDrive) None
        +atender_siguiente(asesor_id: int) TestDrive
        +pendientes(asesor_id: int) int
    }

    class PilaSimulaciones {
        -cima: Nodo
        -cantidad: int
        +apilar(plan: PlanCredito) None
        +desapilar() PlanCredito
        +ver_cima() PlanCredito
        +esta_vacia() bool
    }

    class NodoArbol {
        +moto: Moto
        +izquierdo: NodoArbol
        +derecho: NodoArbol
    }

    class ArbolMotosPorPrecio {
        -raiz: NodoArbol
        +insertar(moto: Moto) None
        +buscar_rango(minimo: int, maximo: int) list~Moto~
        +inorden() list~Moto~
    }

    AgendaTestDrives o-- "*" ColaTestDrives : una por asesor
    ColaTestDrives o-- Nodo
    PilaSimulaciones o-- Nodo
    ArbolMotosPorPrecio o-- NodoArbol
    NodoArbol --> NodoArbol : hijos
    Nodo --> Nodo : siguiente
```
