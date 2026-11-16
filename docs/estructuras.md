
# Estructuras de datos

## Cola de test drives

La clase `ColaTestDrives` implementa una cola FIFO (First In, First Out) mediante
una lista enlazada simple.

Mantiene referencias al primer nodo (`_frente`), al último nodo (`_final`) y
la cantidad de elementos (`_cantidad`).

La clase permite agregar test drives al final, retirar el primero, consultar
el elemento del frente y recorrer los elementos en orden de llegada.

### Complejidad algorítmica

| Operación | Complejidad | Justificación |
|---|---|---|
| `encolar()` | O(1) | Agrega el nodo usando la referencia al final. |
| `desencolar()` | O(1) | Retira el primer nodo y actualiza el frente. |
| `frente()` | O(1) | Consulta directamente el primer nodo. |
| `esta_vacia()` | O(1) | Comprueba si el frente es `None`. |
| `len()` | O(1) | Devuelve el contador de elementos. |
| `__iter__()` | O(n) | Recorre los nodos de la cola. |

## Agenda de test drives por asesor

La clase `AgendaTestDrives` utiliza un diccionario que relaciona el identificador
de cada asesor con su propia `ColaTestDrives`.

Esto permite mantener independientes los turnos de cada asesor.

| Operación | Complejidad | Justificación |
|---|---|---|
| `encolar()` | O(1) promedio | Busca la cola en el diccionario y agrega el nodo. |
| `siguiente()` | O(1) promedio | Busca la cola y retira el primer elemento. |
| `pendientes()` | O(1) promedio | Busca la cola y consulta su contador. |
