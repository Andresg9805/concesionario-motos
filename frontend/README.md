# Frontend (Angular)

Página de Candela Motors hecha en Angular 22 con Angular Material.

## Cómo correrlo

Se necesita Node 22 o más nuevo.

```
cd frontend
npm install
npm start
```

La página abre en `http://localhost:4200`. Consume la API del backend en `http://localhost:8000` (se cambia en `src/environments/environment.ts`).

## Comandos

| Comando | Para qué |
|---|---|
| `npm start` | Corre la página en modo desarrollo |
| `npm run build` | Compila para producción en `dist/` |
| `npm test` | Corre las pruebas con Vitest |

## Cómo está organizado

```
src/app/
├── core/        servicios compartidos: ApiService, sesión con JWT, interceptor y marcas
├── layout/      encabezado (menú y selector de marca) y pie de página
└── paginas/     una carpeta por pantalla: inicio, motos, detalle, accesorios, seguimiento, ingresar, 404
```

## Colores de las marcas

Los colores salen de los wireframes: Honda `#CC0000`, Kawasaki `#69BE28` y Yamaha `#0055B8`. Al elegir una marca arriba, toda la página cambia al color de esa marca (el atributo `data-marca` del `body` cambia la variable `--color-marca`).
