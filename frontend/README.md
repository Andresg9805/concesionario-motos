# Frontend (Angular)

Página de Candela Motors hecha en Angular 22. El diseño es el del wireframe de Nico (`docs/wireframes/`): Tailwind CSS 4 con los mismos colores y clases, íconos de Lucide y las ilustraciones SVG de las motos y los accesorios.

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
├── core/        modelos, datos de prueba y servicios (catálogo, filtros, atención, marca, sesión, API)
├── shared/      piezas reutilizables: tarjeta de moto, siluetas SVG, íconos, formato de pesos
├── layout/      encabezado, pie de página y avisos
├── dialogos/    cotizar / test drive e iniciar sesión / crear cuenta
└── paginas/     inicio (portada, marcas, catálogo, accesorios, cotizar) y página 404
```

## Colores de las marcas

Los tokens de color son los del wireframe (`src/styles.css`). Al elegir una marca en "Elige tu marca", el atributo `data-brand` del `<html>` cambia y toda la página toma la paleta de Honda, Kawasaki o Yamaha. La marca elegida se guarda en el navegador.

## Datos de prueba

Por ahora las motos, los accesorios y los asesores salen de `src/app/core/datos-prueba.ts` (los mismos del wireframe, con los tipos Naked, Doble propósito, Trail y Deportiva). Cuando estén los endpoints, los servicios de `core/` pasan a usar `ApiService` y las pantallas no cambian.
