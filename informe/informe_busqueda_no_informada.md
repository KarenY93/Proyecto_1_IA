# Proyecto 1: Asignación de Horarios Universitarios
## Módulo de Búsqueda No Informada (BFS, Costo Uniforme, IDDFS)

**Materia:** Inteligencia Artificial  
**Semestre:** 2026-2  

### 1. Introducción

En este módulo desarrollamos las tres estrategias de búsqueda no informada requeridas por el proyecto para resolver el problema de construcción de horarios universitarios: búsqueda en amplitud (BFS), búsqueda de costo uniforme y búsqueda en profundidad iterativa (IDDFS).

A diferencia del método informado, estas estrategias no cuentan con una función heurística que estime la distancia restante hacia la meta, por lo que su avance se basa únicamente en el orden en que se generan los nodos o por el costo acumulado g(n).

### 2. Formulación del Problema y Espacio de Búsqueda

El problema se formuló como un problema de satisfacción de restricciones:

- **Variables:** Cada sesión de clase que requiere asignación horaria.
- **Dominio:** Terna compuesta por día, franja horaria y salón de clases.
- **Restricciones Duras:** Se garantiza que en una misma franja horaria no coincidan dos clases en el mismo salón, que un docente no dicte dos materias simultáneamente y que un grupo de estudiantes no tenga clases cruzadas. Además, cada materia debe programarse una sola vez.
- **Restricción Blanda:** Se penaliza con 5 unidades adicionales cada asignación que coincida con la franja que el docente reportó como no disponible (costo de paso igual a 6, frente al costo base de 1).

Decidimos que para poder reducir el espacio de búsqueda, se estableciera un orden fijo para asignar las materias. De esta manera, cada estado parcial se alcanza por un único camino, lo que permite organizar la búsqueda como un árbol sin ciclos y evita tener que guardar una lista de estados que ya fueron visitados.

### 3. Algoritmos Implementados

### 3.1. Búsqueda en Amplitud (BFS)

Este algoritmo recorre los estados por niveles, es decir, primero explora las asignaciones de una materia, luego las de dos y así sucesivamente hasta encontrar una solución completa.
Para manejar los estados pendientes se utilizó una cola FIFO mediante deque, donde el primero en entrar es el primero en ser explorado. De esta manera, BFS encuentra primero una solución con la menor profundidad posible, pero no necesariamente la de menor costo, ya que no tiene en cuenta las penalizaciones docentes al elegir qué estado explorar.

### 3.2. Búsqueda de Costo Uniforme

El algoritmo de costo uniforme siempre busca explorar primero el estado que tenga el menor costo acumulado g(n), con el objetivo de encontrar la solución de menor costo posible.
Manejamos los estados pendientes utilizando un diccionario que los agrupa según su costo, permitiendo seleccionar primero los de menor valor sin tener que ordenar toda la lista.
Cada asignación tiene un costo de 1, pero si el profesor no está disponible en esa franja, se agrega una penalización de 5, dando un costo total de 6. Así, el algoritmo favorece las asignaciones que respetan la disponibilidad de los profesores y busca reducir el costo total de la solución.

### 3.3. Búsqueda en Profundidad Iterativa (IDDFS)

Este algoritmo combina la búsqueda en profundidad con la búsqueda por niveles, aumentando poco a poco el límite de profundidad hasta encontrar una solución.
Se implementó de forma recursiva y, como todas las soluciones completas requieren asignar todas las materias, el límite inicial se establece por defecto en esa cantidad.

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

### 5. Conclusiones

Los resultados confirman que mientras BFS y Costo Uniforme son adecuados únicamente para instancias pequeñas debido al costo en memoria y tiempo derivado de su exploración por niveles, Profundidad Iterativa resulta rápida en problemas con baja saturación de recursos pero carece de capacidad para optimizar restricciones blandas. Este comportamiento resalta la necesidad de recurrir a técnicas de búsqueda informada para problemas de mayor escala que requieran soluciones de costo mínimo.