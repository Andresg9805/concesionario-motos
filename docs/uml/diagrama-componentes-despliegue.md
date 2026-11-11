# Diagramas de componentes y despliegue: Candela Motors

Las fuentes en Mermaid están en `docs/uml/fuentes/`. Si algo cambia, se edita la fuente y se vuelve a exportar la imagen.

## 1. Diagrama de componentes

Muestra cómo está armado el sistema por dentro con la arquitectura hexagonal.

- **Frontend Angular:** las páginas usan servicios HTTP para hablar con la API. Un guard y un interceptor ponen el token JWT en cada petición. El widget de Wompi se abre en el navegador y el pago va directo a Wompi, así los datos de la tarjeta nunca pasan por nuestro backend.
- **Adaptadores de entrada:** los routers REST, la autenticación JWT y el webhook de pagos. Solo reciben la petición, validan los datos y llaman al caso de uso.
- **Capa de aplicación:** los casos de uso, que coordinan el trabajo usando los puertos.
- **Capa de dominio:** las entidades con sus reglas, los puertos (interfaces) y las estructuras propias (cola, pila y árbol). No depende de ninguna otra capa.
- **Adaptadores de salida:** implementan los puertos. Los repositorios usan SQLAlchemy sobre SQLite, los reportes usan DuckDB, el cliente de la TRM consulta datos.gov.co con circuit breaker y la pasarela habla con Wompi.

La flecha punteada "implementado por" es la idea central de la arquitectura hexagonal: el dominio define qué necesita (el puerto) y la infraestructura decide cómo se hace. Por eso podemos cambiar SQLite por otra base de datos, o Wompi por otra pasarela, sin tocar el dominio.

![Diagrama de componentes](diagrama-componentes.png)

```mermaid
flowchart TB
    subgraph FRONT["Frontend Angular"]
        UI["Páginas y componentes"]
        GUARD["Guard e interceptor JWT"]
        SRV["Servicios HTTP"]
        WIDGET["Widget de pago Wompi"]
    end

    subgraph BACK["Backend FastAPI"]
        subgraph ENTRADA["Adaptadores de entrada"]
            API["Routers REST"]
            AUTH["Autenticación JWT"]
            HOOK["Webhook de pagos"]
        end
        subgraph APP["Capa de aplicación"]
            CU["Casos de uso"]
        end
        subgraph DOM["Capa de dominio"]
            ENT["Entidades y reglas"]
            PUERTOS["Puertos"]
            EST["Estructuras propias"]
        end
        subgraph INFRA["Adaptadores de salida"]
            REPO["Repositorios SQLAlchemy"]
            REP["Reportes DuckDB"]
            TRM["Cliente TRM con circuit breaker"]
            PAS["Pasarela Wompi"]
        end
    end

    DB[("SQLite")]
    GOV(["datos.gov.co"])
    WOMPI(["Wompi sandbox"])

    UI --> SRV
    GUARD --> SRV
    SRV -- "HTTP JSON" --> API
    SRV -- "HTTP JSON" --> AUTH
    API --> CU
    AUTH --> CU
    HOOK --> CU
    CU --> ENT
    CU --> PUERTOS
    ENT --> EST
    PUERTOS -. "implementado por" .-> REPO
    PUERTOS -. "implementado por" .-> REP
    PUERTOS -. "implementado por" .-> TRM
    PUERTOS -. "implementado por" .-> PAS
    REPO --> DB
    REP -- "lee" --> DB
    TRM -- "HTTPS" --> GOV
    PAS -- "HTTPS" --> WOMPI
    WIDGET -- "pago" --> WOMPI
    WOMPI -- "aviso firmado" --> HOOK
```

## 2. Diagrama de despliegue

Muestra dónde corre cada parte cuando el sistema está funcionando.

- **Equipo del usuario:** el navegador descarga la página desde nginx y llama a la API en el puerto 8000.
- **Servidor con Docker Compose:** dos contenedores, uno con nginx sirviendo Angular ya compilado y otro con uvicorn corriendo FastAPI. La base de datos SQLite queda en un volumen para que no se pierda al reiniciar los contenedores. Las llaves de Wompi y el secreto del JWT se leen del archivo `.env`, que nunca se sube al repositorio.
- **Servicios externos:** el backend consulta la TRM en datos.gov.co y la API de Wompi en ambiente de pruebas. Wompi avisa el resultado del pago con un webhook, y como trabajamos en un computador local se usa un túnel (ngrok o Cloudflare Tunnel) que reenvía ese aviso a `/pagos/webhook`.
- **GitHub:** en cada pull request, GitHub Actions corre `ruff` y `pytest`.

![Diagrama de despliegue](diagrama-despliegue.png)

```mermaid
flowchart TB
    subgraph PC["Equipo del usuario"]
        NAV["Navegador web"]
    end

    subgraph HOST["Servidor con Docker Compose"]
        subgraph CF["Contenedor frontend"]
            NGINX["nginx :80 con Angular compilado"]
        end
        subgraph CB["Contenedor backend"]
            UV["uvicorn :8000 con FastAPI"]
        end
        ENV["Archivo .env con llaves"]
        VOL[("Volumen con concesionario.db")]
    end

    TUN["Túnel ngrok o Cloudflare"]
    WOMPI(["Wompi sandbox"])
    GOV(["datos.gov.co"])

    subgraph GH["GitHub"]
        REPO["Repositorio"]
        CI["GitHub Actions: ruff y pytest"]
    end

    NAV -- "HTTP :80" --> NGINX
    NAV -- "API REST :8000" --> UV
    NAV -- "widget de pago" --> WOMPI
    ENV -.-> UV
    UV --> VOL
    UV -- "HTTPS" --> GOV
    UV -- "HTTPS" --> WOMPI
    WOMPI -- "webhook" --> TUN
    TUN -- "reenvía a /pagos/webhook" --> UV
    REPO -- "cada PR" --> CI
```
