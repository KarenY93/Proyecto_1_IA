# Proyecto 1: Asignación de Horarios Universitarios
## Módulo de Búsqueda No Informada (BFS, Costo Uniforme, IDDFS)

**Materia:** Inteligencia Artificial  
**Semestre:** 2026-2  

---

### 1. Introducción

En este módulo se desarrollaron y evaluaron tres estrategias de búsqueda no informada para resolver el problema de construcción de horarios universitarios: búsqueda en amplitud (BFS), búsqueda de costo uniforme y búsqueda en profundidad iterativa (IDDFS).

A diferencia de los métodos informados, estas estrategias no cuentan con una función heurística que estime la distancia restante hacia la meta, por lo que su avance se rige únicamente por el orden sistemático de generación de nodos o por el costo acumulado g(n) alcanzado en cada estado. Los tres algoritmos fueron programados desde cero en Python sin utilizar librerías externas para la gestión de colas de prioridad.

---

### 2. Formulación del Problema y Espacio de Búsqueda

El problema se formuló como un problema de satisfacción de restricciones (CSP):

- **Variables:** Cada sesión de clase que requiere asignación horaria.
- **Dominio:** Ternas compuestas por día, franja horaria y salón de clases.
- **Restricciones Duras:** Se garantiza que en una misma franja horaria no coincidan dos clases en el mismo salón, que un docente no dicte dos materias simultáneamente y que un grupo de estudiantes no tenga clases cruzadas. Además, cada materia debe programarse exactamente una vez.
- **Restricción Blanda:** Se penaliza con 5 unidades adicionales cada asignación que coincida con la franja que el docente reportó como no disponible (costo de paso igual a 6, frente al costo base de 1).

Para acotar el espacio de búsqueda se definió un orden secuencial fijo para la asignación de las materias. Bajo este enfoque, cada estado parcial solo puede ser alcanzado mediante un camino único, lo que modela el espacio de búsqueda como un árbol libre de ciclos y evita la necesidad de mantener tablas de estados cerrados.

---

### 3. Algoritmos Implementados

#### 3.1. Búsqueda en Amplitud (BFS)
El algoritmo recorre el espacio de búsqueda nivel por nivel, evaluando primero todos los estados con una clase programada, luego los de dos clases, y así sucesivamente. Se implementó utilizando una cola FIFO basada en `deque` de la librería estándar. BFS garantiza encontrar una solución con la mínima profundidad posible; no obstante, al no evaluar el costo acumulado, devuelve la primera solución completa que encuentra independientemente de si incluye penalizaciones docentes.

#### 3.2. Búsqueda de Costo Uniforme
Costo uniforme prioriza en cada iteración el estado con el menor costo acumulado g(n). Ante la restricción de no emplear librerías externas como `heapq`, y aprovechando que los costos de paso son valores enteros discretos (1 o 6), la frontera de búsqueda se implementó mediante un diccionario indexado por costo (`{costo: [estados]}`). Esto permite extraer el nodo de menor costo de forma eficiente sin necesidad de ordenar listas en cada paso. Es el único de los tres algoritmos no informados que asegura una solución de costo óptimo respecto a las preferencias docentes.

#### 3.3. Búsqueda en Profundidad Iterativa (IDDFS)
Combina la baja exigencia de memoria de la búsqueda en profundidad con la completitud de la búsqueda por niveles. Se implementó de manera recursiva aumentando el límite de profundidad de forma progresiva. Dado que en este problema todas las soluciones completas se encuentran a una profundidad igual al número total de materias, el límite inicial se configuró por defecto en dicha profundidad, manteniendo disponible la opción de ejecución clásica desde profundidad cero.

---

### 4. Pruebas y Análisis de Rendimiento

Se realizaron evaluaciones tanto con instancias reducidas como con el conjunto de datos completo de 20 materias.

#### Instancia Pequeña (3 clases, 2 franjas, 2 salones)
En un escenario donde el docente asignado a una de las materias reportó no disponibilidad en la primera franja:
- BFS encontró solución en 4 nodos explorados con un costo total de 8 unidades (asignó la clase en la franja bloqueada al ignorar el costo).
- IDDFS exploró 4 nodos y obtuvo igualmente un costo de 8 unidades.
- Costo Uniforme exploró 3 nodos y alcanzó la meta con un costo de 3 unidades, eligiendo la franja alternativa libre de penalización.

#### Instancia Completa (20 clases, 20 franjas, 20 salones)
Al incrementar la escala del problema se evidenciaron las diferencias estructurales entre los métodos:
- BFS y Costo Uniforme: A partir de 5 clases programadas, el número de ramas generadas crece exponencialmente, superando el tope de 20.000 nodos explorados sin alcanzar una solución en tiempo razonable.
- Profundidad Iterativa: Logró resolver las 20 clases en 21 nodos explorados y 0.0002 segundos, ya que en el dataset real la disponibilidad de salones permite avanzar en profundidad sin requerir retrocesos frecuentes. Sin embargo, al no considerar costos acumulados, arrojó un costo final de 25 unidades debido a cruces con horarios bloqueados por docentes.

---

### 5. Conclusiones

Los resultados confirman que mientras BFS y Costo Uniforme son adecuados únicamente para instancias pequeñas debido al costo en memoria y tiempo derivado de su exploración por niveles, Profundidad Iterativa resulta rápida en problemas con baja saturación de recursos pero carece de capacidad para optimizar restricciones blandas. Este comportamiento resalta la necesidad de recurrir a técnicas de búsqueda informada para problemas de mayor escala que requieran soluciones de costo mínimo.
