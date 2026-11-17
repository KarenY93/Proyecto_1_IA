# Proyecto 1: Asignación de Horarios Universitarios
## Módulo de Búsqueda Informada (A*)

**Materia:** Inteligencia Artificial  
**Semestre:** 2026-2  

### 1. Introducción

El siguiente documento describe el desarrollo y las pruebas del motor de búsqueda informada para el problema de asignación de horarios académicos universitarios. El objetivo del problema consiste en asignar a cada sesión de clase un día, una franja horaria y un salón específico, cumpliendo con las restricciones duras del sistema (evitar cruces de profesor, de salón y de grupos de estudiantes) y bajando el costo derivado de las restricciones blandas (la no disponibilidad horaria reportada por los docentes).

Para este módulo se seleccionó e implementó el algoritmo A* desde cero en Python, sin el uso de librerías externas de búsqueda o colas de prioridad predefinidas, de acuerdo con los lineamientos del proyecto.

### 2. Representación del Estado y Espacio de Búsqueda

El espacio de búsqueda se modeló a partir de una asignación progresiva de materias:

**Variables:** Cada curso o clase a programar (identificador de materia, profesor asignado y grupo de estudiantes).
**Dominio:** Las combinaciones posibles de día, franja horaria y salón. Con 5 días, 4 franjas por día y 20 salones, existen hasta 400 opciones de asignación por clase.
**Estado:** Se representa mediante el conjunto de asignaciones realizadas hasta el momento y el registro de los recursos que ya se encuentran ocupados en cada bloque de tiempo.
**Transición:** Un paso de búsqueda consiste en tomar la siguiente clase pendiente y asignarla a una terna (día, franja, salón) que no presente conflicto con las clases ya programadas.

Para estructurar la búsqueda se fijó un orden estricto de programación de las clases (se asigna primero la clase 1, luego la clase 2, y así sucesivamente). Dado que un horario completo requiere obligatoriamente la programación de todas las materias, fijar el orden de las asignaciones no elimina soluciones posibles y asegura que el espacio de búsqueda se comporte como un árbol, evitando que el algoritmo alcance un mismo estado por diferentes ramas.

### 3. Función Heurística y Costo Acumulado

El algoritmo A* evalúa cada nodo mediante la función f(n) = g(n) + h(n):

El costo acumulado g(n) se definió asignando un costo base de 1 por cada clase programada en el horario. Si una clase se asigna en la franja que el docente registró como no disponible, se aplica una penalización de 5 unidades adicionales (costo de paso igual a 6), guiando al algoritmo a evitar dichos horarios siempre que existan alternativas libres.

La heurística h(n) se diseñó como el número de clases que aún quedan pendientes por asignar en el estado actual:
h(n) = total_clases - clases_asignadas

Esta función es admisible debido a que cada materia restante requerirá forzosamente al menos una asignación en el horario, lo que sumará un mínimo de 1 unidad al costo real del camino. Por consiguiente, la estimación h jamás excede el costo real para alcanzar la meta. Asimismo, es consistente porque al avanzar un nivel en el árbol, la heurística disminuye exactamente en 1 unidad mientras que el costo real se incrementa en al menos 1 unidad.

En caso de empates en el valor de f(n), el algoritmo prioriza los nodos que tienen un menor valor de h(n), lo que permite avanzar de manera directa en profundidad hacia la meta una vez identificadas ramas libres de penalizaciones.

### 4. Implementación del Algoritmo A*

La implementación se encuentra en el archivo `algoritmos/a_estrella.py`. Para cumplir con la restricción de no emplear librerías externas como `heapq`, la frontera se maneja con una lista estándar en la que en cada ciclo se localiza y extrae el nodo con el menor valor de evaluación f(n).

El flujo del algoritmo contempla los siguientes pasos:
1. Verificación previa de factibilidad para detectar incoherencias iniciales (como exceso de clases respecto a los salones y franjas disponibles).
2. Inicialización del nodo raíz con el estado inicial vacío y su correspondiente valor heurístico.
3. Ciclo principal de extracción del nodo más prometedor de la frontera.
4. Verificación del límite de nodos explorados para evitar ejecuciones indefinidas en instancias sin solución.
5. Verificación de meta: si todas las materias han sido asignadas, se retorna la solución y las métricas de ejecución.
6. En caso contrario, se generan los sucesores válidos para la siguiente materia pendiente, calculando el nuevo costo acumulado g y el valor heurístico h para cada hijo generado.

El resultado se devuelve en un diccionario estructurado que incluye la solución encontrada, el costo total, el tiempo de ejecución en segundos y el número de nodos explorados, lo que permite su integración con la interfaz gráfica.

### 5. Pruebas y Análisis de Resultados

Se realizaron pruebas tanto en escenarios controlados para validar la lógica como con el conjunto completo de datos de 20 materias provisto en el proyecto.

En las pruebas unitarias se verificaron casos límite:
- Manejo correcto de entradas vacías y de una sola clase.
- Detección de incompatibilidades cuando dos materias comparten docente o grupo.
- Elección preferente de franjas disponibles frente a franjas bloqueadas por el docente, comprobando la minimización del costo.
- Interrupción controlada por tope de nodos cuando se ingresa un límite estricto.

Al ejecutar el algoritmo sobre el problema completo de 20 clases, 20 franjas y 20 salones, A* encontró una asignación válida en 21 nodos explorados con un tiempo promedio de 0.005 segundos y un costo total de 20 unidades. Este resultado indica que ninguna clase fue asignada en horario no disponible de los profesores, alcanzando el costo mínimo absoluto.

Al comparar este desempeño con los algoritmos no informados:
- Amplitud (BFS) y Costo Uniforme se ven limitados por el crecimiento exponencial del árbol, superando los 20.000 nodos explorados sin completar las 20 clases en el dataset real.
- Profundidad Iterativa (IDDFS) logra resolver la instancia en 21 nodos, pero al no considerar el costo acumulado asigna materias en franjas no disponibles de profesores cuando se presentan en su recorrido (costo resultante de 25).
- A* combinó la rapidez de avance en profundidad con la optimización de costo, obteniendo el horario sin violaciones en tiempo mínimo.

### 6. Conclusiones

La implementación de A* demostró ser la alternativa más eficiente y equilibrada para este problema. La combinación de una heurística admisible basada en clases pendientes junto con la ruptura de simetrías en los salones permitió resolver el problema de 20 materias en milisegundos y con el menor número de nodos, garantizando el cumplimiento estricto de todas las restricciones duras y la satisfacción de las preferencias de los docentes.
