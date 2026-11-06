# Guía para trabajar con Git y GitHub en el proyecto

Esta guía explica cómo trabajamos los tres en el repositorio sin dañarnos el trabajo entre nosotros. Léanla completa una vez y tengan a la mano las secciones de **Problemas comunes** y **Comandos de bolsillo**.

Si algo sale raro y no está aquí, **no intenten arreglarlo con comandos que encuentren en internet**. Manden captura del error al grupo y lo resolvemos juntos.

---

## 1. Configuración inicial (solo se hace una vez)

**Paso 1.** Instalar Git desde https://git-scm.com, dejando todas las opciones por defecto.

**Paso 2.** Instalar VS Code desde https://code.visualstudio.com

**Paso 3.** Abrir una terminal (en VS Code: `Terminal > New Terminal`) y configurar su nombre y el correo de su cuenta de GitHub:

```
git config --global user.name "Nombre Apellido"
git config --global user.email "correo-de-github@ejemplo.com"
```

**Paso 4.** Clonar el repositorio en la carpeta donde quieran tener el proyecto:

```
git clone https://github.com/Andresg9805/concesionario-motos.git
cd concesionario-motos
```

**Paso 5.** La primera vez que hagan `git push` se abre el navegador para iniciar sesión en GitHub. GitHub **no** acepta la contraseña escrita en la terminal, siempre es por el navegador.

Para comprobar que todo quedó bien:

```
git --version
git config --global --list
```

---

## 2. Reglas de oro

1. **Nunca trabajar directo en `main`.** Antes de tocar cualquier archivo, crear una rama.
2. **Siempre actualizar `main` antes de crear una rama** (`git pull`).
3. **Una rama = una tarea = un issue.** No mezclar dos tareas en la misma rama.
4. **Commits pequeños y seguidos**, con el formato de la sección 4.
5. **Todo entra a `main` por Pull Request**, y otro integrante lo tiene que aprobar.
6. **Mirar `git status` antes de `git add`**, para no subir archivos que no son.
7. **Hacer `git push` antes de apagar el computador.** Así el trabajo queda guardado en GitHub aunque se dañe el PC.
8. **Nunca usar** `git push --force`, `git reset --hard` ni `git clean` sin preguntar antes en el grupo.

---

## 3. El flujo de cada tarea, paso a paso

### Paso 1: Mover la tarjeta

En el tablero de GitHub Projects, mover su issue de **Backlog** a **In progress**.

### Paso 2: Actualizar main

```
git switch main
git pull
```

### Paso 3: Crear la rama de la tarea

```
git switch -c feature/catalogo-motos
```

### Paso 4: Trabajar y guardar avances

Cada vez que terminen una parte que funcione:

```
git status
git add .
git commit -m "feat(catalogo): listar motos con filtro por marca"
```

Si en `git status` aparece algún archivo que no debería subirse, en lugar de `git add .` agreguen solo los suyos:

```
git add ruta/del/archivo.py
```

### Paso 5: Subir la rama a GitHub

La primera vez:

```
git push -u origin feature/catalogo-motos
```

Las siguientes veces basta con `git push`.

### Paso 6: Abrir el Pull Request

1. En GitHub aparece el botón amarillo **Compare & pull request**. Darle clic.
2. Revisar que diga **base: main ← compare: su-rama**.
3. Poner un título claro, por ejemplo: `Catálogo de motos con filtros`.
4. Llenar la plantilla y al final dejar `Closes #N` (N es el número del issue). Con eso el issue se cierra solo cuando se hace merge.
5. En **Reviewers** (a la derecha) elegir a un compañero.
6. Clic en **Create pull request**.

La tarjeta pasa sola a **In review** en el tablero.

### Paso 7: Revisión

- Si el compañero pide cambios, se hacen **en la misma rama**, con commit y `git push`. El PR se actualiza solo, no hay que abrir otro.
- Si el CI (las pruebas automáticas) sale en rojo, hay que arreglarlo antes del merge.

### Paso 8: Merge

Cuando el PR tenga la aprobación, el autor le da **Merge pull request** → **Confirm merge** → **Delete branch**.

### Paso 9: Limpiar en su computador

```
git switch main
git pull
git branch -d feature/catalogo-motos
```

Listo. La siguiente tarea empieza otra vez desde el paso 1.

---

## 4. Cómo nombrar ramas y commits

Las ramas van como `tipo/descripcion-corta` y los commits como `tipo(área): qué se hizo`, todo en minúscula.

### Ramas

| Tipo | Para qué | Ejemplo |
| --- | --- | --- |
| `feature/` | Funcionalidad nueva | `feature/login-jwt` |
| `fix/` | Arreglar un error | `fix/precio-negativo` |
| `docs/` | Documentación y diagramas | `docs/modelo-entidad-relacion` |
| `test/` | Pruebas | `test/repositorio-motos` |
| `chore/` | Configuración | `chore/docker-compose` |

### Commits

Bien:

- `feat(catalogo): agregar filtro por cilindraje`
- `fix(cotizacion): corregir cálculo de la cuota mensual`
- `docs(uml): agregar diagrama de casos de uso`
- `test(dominio): pruebas de la cola de test drives`

Mal:

- `cambios`
- `ya quedó`
- `asdfg`
- `arreglos varios`

---

## 5. Cómo revisar el PR de un compañero

Un PR se revisa el mismo día que se pide la revisión. Si nadie revisa, el proyecto se frena. Cualquiera de los tres puede aprobar.

1. Abrir el PR y entrar a la pestaña **Files changed**.
2. Leer los cambios. Si algo no se entiende, dar clic en el número de la línea y dejar un comentario.
3. Revisar esta lista:
    - ¿Hace lo que pide el issue?
    - ¿El CI está en verde?
    - ¿No se subieron archivos basura (`__pycache__`, `.env`, bases de datos, `node_modules`)?
    - ¿Los nombres de variables y funciones se entienden?
4. Clic en **Review changes** (arriba a la derecha):
    - **Approve** si todo está bien.
    - **Request changes** si hay que corregir algo, explicando qué.

Los comentarios son sobre el código, no sobre la persona. Siempre con respeto.

---

## 6. Precauciones

La precaución que más conflictos evita es que cada uno trabaje en su propia zona del proyecto. Si necesitan tocar un archivo de la zona de otro, avisen primero en el grupo.

| Integrante | Zona del proyecto |
| --- | --- |
| Andrés | `backend/app/domain/` y `frontend/` (Angular) |
| Laura | `backend/app/infrastructure/db/`, `backend/app/infrastructure/reportes/`, la cola de test drives en `backend/app/domain/estructuras/` (coordinado con Andrés) y la organización de `backend/tests/` |
| Nicolás | `backend/app/application/`, `backend/app/api/`, `backend/app/infrastructure/externos/`, `docs/requisitos/` y los archivos de Docker |

Cada uno escribe las pruebas de su propio código.

- **Ramas cortas.** Un PR no debería durar más de 1 o 2 días abierto. Entre más tiempo pase, más conflictos.
- **Si su rama ya tiene varios días**, tráiganse lo nuevo de `main` con los comandos de abajo.
- **Claves y contraseñas nunca se suben.** Van en un archivo `.env`, que ya está en el `.gitignore`. En el repo solo va el `backend/.env.example` con los nombres de las variables, sin los valores reales.
- **No borrar ni renombrar archivos de otros** sin hablarlo.
- **No subir archivos pesados** como videos, instaladores o imágenes muy grandes.

Para actualizar una rama vieja con lo nuevo de `main`:

```
git switch main
git pull
git switch su-rama
git merge main
```

---

## 7. Problemas comunes y cómo resolverlos

### "Estaba trabajando en main sin darme cuenta" (todavía no hice commit)

No pasa nada, los cambios se pasan a una rama nueva:

```
git switch -c feature/nombre-de-la-tarea
```

### "Hice commit en main sin darme cuenta" (todavía no hice push)

Crear la rama desde ahí para no perder el trabajo:

```
git switch -c feature/nombre-de-la-tarea
git push -u origin feature/nombre-de-la-tarea
```

Después **avisen en el grupo** para dejar su `main` local igual al de GitHub. No lo intenten solos.

### "Me sale error al hacer push a main" (protected branch)

Es normal, `main` está protegida. Están en `main`: creen una rama como en el caso de arriba y suban esa.

### "Me sale rejected o non-fast-forward al hacer push en mi rama"

Alguien más subió cambios a esa rama, o la editaron desde GitHub. Primero traer lo nuevo y después subir:

```
git pull
git push
```

### "Me salió un conflicto" (CONFLICT)

Pasa cuando dos personas cambiaron las mismas líneas. El archivo queda así:

```
<<<<<<< HEAD
lo que tienen ustedes
=======
lo que viene de la otra rama
>>>>>>> main
```

1. Abrir el archivo en VS Code. Arriba del conflicto salen las opciones **Accept Current**, **Accept Incoming** y **Accept Both**.
2. Escoger la correcta o dejar el código bien a mano. Si no están seguros, **llamen a quien escribió la otra parte**.
3. Verificar que no queden las marcas `<<<<<<<`, `=======` ni `>>>>>>>`.
4. Guardar y terminar con:

```
git add .
git commit -m "fix: resolver conflicto con main"
git push
```

### "El PR dice: This branch has conflicts that must be resolved"

Se resuelve en su computador:

```
git switch main
git pull
git switch su-rama
git merge main
```

Resolver el conflicto como en el caso anterior y luego `git push`.

### "Me equivoqué en el mensaje del último commit" (todavía no hice push)

```
git commit --amend -m "mensaje correcto"
```

Si ya hicieron push, déjenlo así. No vale la pena arreglarlo.

### "Agregué con git add un archivo que no era" (todavía no hice commit)

```
git restore --staged ruta/del/archivo
```

### "Quiero botar los cambios de un archivo y dejarlo como estaba"

Ojo: los cambios se pierden y no se pueden recuperar.

```
git restore ruta/del/archivo
```

### "fatal: not a git repository"

La terminal no está en la carpeta del proyecto. Abran la carpeta `concesionario-motos` en VS Code y abran la terminal desde ahí.

### "Hice pull y ahora algo no funciona"

No borren nada. Avisen en el grupo qué dejó de funcionar y desde qué PR.

---

## 8. Comandos de bolsillo

| Comando | Para qué sirve |
| --- | --- |
| `git status` | Ver qué archivos cambiaron y en qué rama estoy |
| `git switch main` | Pasarse a la rama main |
| `git pull` | Traer lo último de GitHub |
| `git switch -c nombre` | Crear una rama nueva y pasarse a ella |
| `git switch nombre` | Pasarse a una rama que ya existe |
| `git branch` | Ver mis ramas (la actual tiene `*`) |
| `git add .` | Preparar todos los cambios para el commit |
| `git add archivo` | Preparar solo un archivo |
| `git commit -m "mensaje"` | Guardar los cambios con un mensaje |
| `git push` | Subir mis commits a GitHub |
| `git push -u origin nombre` | Subir una rama nueva por primera vez |
| `git log --oneline` | Ver los últimos commits |
| `git merge main` | Traer a mi rama lo nuevo de main |
| `git branch -d nombre` | Borrar una rama local que ya tuvo merge |

---

## 9. Resumen

**Actualizar main → crear rama → commits pequeños → push → Pull Request con `Closes #N` → revisión → merge → borrar rama → siguiente tarea.**

Si la revisión pide cambios, se corrigen en la misma rama y se vuelve a hacer push. Solo con la aprobación se hace merge a `main`.
