# Búsqueda no informada para la asignación de horarios universitarios

Proyecto 1 – Inteligencia Artificial. Algoritmos: búsqueda en amplitud (BFS), costo uniforme y profundidad iterativa (IDDFS).

## 1. Objetivo

Este informe describe cómo se modeló el problema de construir un horario académico como un problema de búsqueda en espacio de estados, cómo se implementaron tres estrategias de búsqueda no informada **desde cero y sin bibliotecas externas**, qué optimizaciones se aplicaron y qué resultados se obtuvieron al ejecutarlas.

Una búsqueda no informada construye el horario sin usar ninguna estimación de qué asignación es más prometedora: solo conoce las reglas del problema. Los algoritmos exploran estados parciales hasta encontrar uno con todas las clases programadas o hasta agotar los estados alcanzables.

**Resumen de hallazgos**

- Con una muestra pequeña (3 clases, 2 franjas, 2 salones) los tres algoritmos encuentran un horario sin conflictos duros. Costo uniforme es el único que garantiza el menor costo y evitó la franja no disponible del profesor.
- BFS y costo uniforme crecen de forma exponencial: con 20 franjas y 20 salones resuelven 4 clases, pero con 5 agotan el tope de 20 000 nodos. Esto es una propiedad del algoritmo y no un error de implementación.
- Profundidad iterativa resolvió 20 clases en 21 nodos, porque las soluciones abundan y la búsqueda en profundidad llega a una sin retroceder.

## 2. Definición del problema

Es un problema de satisfacción de restricciones (CSP).

- **Variables:** cada clase que debe programarse.
- **Dominio de cada variable:** las combinaciones posibles `(día, franja, salón)`.
- **Restricciones duras** (no pueden violarse):
  - Un salón no puede tener dos clases en el mismo día y franja.
  - Un profesor no puede dictar dos clases en el mismo día y franja.
  - Un grupo no puede tener dos clases en el mismo día y franja.
  - Cada clase se programa exactamente una vez.
- **Restricción blanda** (deseable): un profesor no debería tener clase en la franja que marcó como no disponible. Se modela como penalización en el costo.

## 3. Representación del problema

| Elemento | Definición |
|---|---|
| Estado | Conjunto de asignaciones `(id_clase, día, franja, salón)` realizadas hasta el momento, junto con los recursos ocupados `(día, franja, tipo, id)`. |
| Estado inicial | Ninguna clase asignada. |
| Acción | Asignar la siguiente clase pendiente a una combinación `(día, franja, salón)` que no viole las restricciones duras. |
| Función sucesora | Devuelve un estado nuevo por cada acción válida; el estado padre no se modifica. |
| Prueba de meta | Todas las clases están asignadas. |
| Costo de paso | 1 por cada clase programada, más 5 si cae en la franja no disponible de su profesor. |

### 3.1. Orden fijo de clases: el espacio es un árbol

En cada nivel se asigna siempre la clase `clases[len(estado)]`, es decir, se procesan en un orden fijo. Esto no pierde soluciones, porque toda solución completa debe asignar todas las clases y por tanto puede construirse en ese orden. Además evita generar estados que solo difieren en el orden en que se tomaron las mismas decisiones.

Consecuencia importante: **cada estado se alcanza por un único camino**, de modo que el espacio de búsqueda es un árbol. No existen estados repetidos que detectar, y por eso las implementaciones no necesitan conjuntos de visitados.

### 3.2. Tamaño del espacio de búsqueda

- Profundidad de toda solución: `d` = número de clases (cada acción asigna una clase).
- Factor de ramificación máximo: `b` = número de combinaciones válidas desde un estado. No es constante: depende de los conflictos y de lo que quede disponible.
- Con 20 franjas y 20 salones hay hasta 400 combinaciones por clase, y con 20 clases el árbol tiene del orden de `400^20 ≈ 1,1 × 10^52` hojas antes de aplicar restricciones.
- En la muestra de pruebas (2 franjas × 2 salones) hay 4 combinaciones por clase y `4^3 = 64` hojas como máximo.

## 4. Algoritmos implementados

### 4.1. Búsqueda en amplitud (BFS)

Usa una cola FIFO (una lista con un índice al frente, para no desplazar elementos con `pop(0)`). Expande todos los estados de un nivel antes de pasar al siguiente, por lo que encuentra una solución de profundidad mínima.

- **Completitud:** sí, con ramificación finita (el dominio de días, franjas y salones es finito).
- **Optimalidad:** óptima en profundidad. Como todas las soluciones completas tienen la misma profundidad `d`, BFS devuelve la primera que encuentra, que no es necesariamente la de menor costo cuando hay penalizaciones.
- **Complejidad:** tiempo y memoria `O(b^d)` en el peor caso.

### 4.2. Búsqueda de costo uniforme

Expande primero el estado con menor costo acumulado `g(n)`. La restricción del proyecto prohíbe `heapq`, así que la frontera se guarda en **cubetas por costo**: un diccionario `{costo_acumulado: [nodos]}`. Como los costos de paso son enteros (1 o 6), obtener el menor costo es avanzar un contador, lo que cuesta O(1) amortizado. La prueba de meta se hace al *retirar* el nodo, que es lo que garantiza la optimalidad.

- **Completitud y optimalidad:** sí, porque cada paso cuesta al menos 1 (costos positivos).
- **Complejidad:** `O(b^(1 + C*/ε))`, con `C*` el costo de la solución óptima y `ε` el costo mínimo de paso.
- **Supuesto:** costos enteros. Si cambiaran a decimales habría que usar otra estructura.

### 4.3. Profundidad iterativa (IDDFS)

Ejecuta búsquedas en profundidad con límite creciente. La pila de recursión es el camino actual, por lo que la memoria es proporcional a la profundidad.

- **Completitud:** sí para un espacio finito.
- **Optimalidad:** encuentra una solución de profundidad mínima; no garantiza costo mínimo porque no usa `g(n)` para decidir el orden.
- **Complejidad:** tiempo `O(b^d)` y memoria `O(bd)`.

### 4.4. Comparación

| Algoritmo | Orden de exploración | Completo | Óptimo | Memoria (peor caso) |
|---|---|---|---|---|
| BFS | Menor profundidad primero | Sí | En profundidad | `O(b^d)` |
| Costo uniforme | Menor costo acumulado primero | Sí (costos positivos) | En costo | `O(b^(1 + C*/ε))` |
| IDDFS | Límites de profundidad crecientes | Sí | En profundidad | `O(bd)` |

## 5. Optimizaciones aplicadas

Todas se implementaron con listas, conjuntos y diccionarios de Python; la lógica solo importa `time` para medir la duración. El módulo `algoritmos/comun.py` concentra el código compartido (sucesores, costo de paso, prechequeo y formato del resultado) para que los tres algoritmos exploren exactamente el mismo espacio.

| Optimización | Qué hace | Por qué es válida |
|---|---|---|
| Sin conjunto de visitados | Se eliminó el conjunto de estados de BFS y el diccionario de mejores costos de costo uniforme. | El orden fijo hace que el espacio sea un árbol: nunca descartaban nada y solo gastaban memoria y tiempo. |
| Prueba de meta al generar (BFS) | Se devuelve la primera meta generada, sin esperar a retirarla. | Todas las metas están a la misma profundidad, así que la primera generada ya es de profundidad mínima. Ahorra expandir el último nivel. |
| Cubetas por costo (costo uniforme) | Reemplaza el recorrido de toda la lista por un diccionario indexado por costo. | Los costos son enteros positivos; la selección del menor pasa de `O(F)` a O(1) amortizado. |
| Atajo por cota inferior (costo uniforme) | Si un estado completo generado cuesta exactamente `total_clases`, se devuelve. | Ninguna solución puede costar menos de 1 por clase, así que ya es óptima. |
| Primer límite en `d` (IDDFS) | Por defecto empieza en el límite `total_clases`. | Toda meta está a profundidad exacta `d`; un límite menor no puede encontrarla y solo obligaría a recorrer el árbol hasta ese nivel. El parámetro `modo_clasico` conserva el IDDFS puro desde 0. |
| Simetría de salones | Solo se prueban los salones ya usados y el primer salón nunca usado. | Si los salones son intercambiables, horarios que difieren solo en el nombre de un salón sin usar son equivalentes. Si se agregan capacidades o tipos de salón, debe desactivarse. |
| Prechequeo de factibilidad | Detecta imposibilidades evidentes: más clases que pares (franja, salón), o un profesor o grupo con más clases que franjas. | Son condiciones necesarias; si fallan, no hay solución y se responde con 0 nodos. |
| Tope de nodos (`max_nodos`) | Si se alcanza, devuelve `limite_alcanzado = True`. | Evita que BFS y costo uniforme agoten la memoria del equipo y permite reportar el agotamiento. |
| Estado liviano | La clave de igualdad se calcula solo si se necesita; el conjunto de ids se construye de forma incremental; profesor y grupo se verifican una vez por franja y no por cada salón. | No cambia la semántica, solo reduce el trabajo por nodo. |

Se verificó la equivalencia de las versiones optimizadas con las originales sobre 200 casos aleatorios pequeños: coinciden en si hay solución y, en costo uniforme, en el costo óptimo.

### 5.1. Conteo de nodos

Para comparar ejecuciones se registran los nodos explorados, el tiempo (`time.perf_counter`) y si se encontró solución. En BFS y costo uniforme se cuenta un nodo cuando se retira de la frontera; en IDDFS se cuenta cada llamada recursiva, y los estados se vuelven a contar cuando un límite posterior repite la búsqueda.

## 6. Pruebas y resultados

### 6.1. Casos de prueba

| Caso | Entrada | Resultado esperado |
|---|---|---|
| Mínimo | Una clase, una franja y un salón. | Encuentra una asignación válida. |
| Soluble | Dos clases comparten profesor; hay un salón y dos franjas. | Las asigna en franjas distintas. |
| Sin solución | Dos clases comparten profesor y solo hay una franja, aunque existan dos salones. | `encontro_solucion: False` y `solucion: None`. |
| Preferencia blanda (costo uniforme) | Una franja no disponible para el profesor y otra disponible. | Escoge la franja disponible, de menor costo. |

El caso sin solución se ejecuta con el prechequeo desactivado (`prechequeo=False`); de lo contrario el prechequeo responde sin recorrer el árbol y la prueba dejaría de verificar la búsqueda. La función `validar_horario` comprueba que cada clase se asigne una vez y que no haya conflictos de salón, profesor ni grupo.

### 6.2. Ejecución con los datos del proyecto

Se leyeron 20 clases, 20 franjas, 20 salones y 20 profesores. Para la prueba se usó una muestra de **3 clases, 2 franjas y 2 salones**. Resultados medidos al ejecutar los scripts (Python 3.13, Windows):

| Métrica | BFS | Costo uniforme | IDDFS |
|---|---:|---:|---:|
| Encontró solución | Sí | Sí | Sí |
| Nodos explorados | 4 | 3 | 4 |
| Tiempo de ejecución | 0,0001 s | 0,0001 s | 0,0001 s |
| Conflictos duros | 0 | 0 | 0 |
| Clases en franja no disponible | 1 | 0 | 1 |

Los tres horarios cumplen las restricciones duras. La diferencia aparece en la restricción blanda: BFS e IDDFS devolvieron un horario con una clase en una franja que el profesor marcó como no disponible (costo 3 + 5 = 8), mientras que costo uniforme devolvió uno sin violaciones (costo 3). BFS e IDDFS optimizan la profundidad, que es igual para todas las soluciones, y no consultan el costo. Costo uniforme sí lo usa, por eso es el único que lo minimiza.

Algunas asignaciones de la muestra: en BFS, C01 (Álgebra Lineal) quedó el lunes 08:00-10:00 en el Salón 101; en costo uniforme, C01 quedó el lunes 10:00-12:00 y evitó esa franja.

### 6.3. Escalabilidad

Se midió el comportamiento al aumentar el número de clases con datos sintéticos del tamaño real del problema: 20 franjas, 20 salones, profesores `P1`–`P5`, grupos `G1`–`G4` y sin penalizaciones. BFS y costo uniforme se ejecutaron con un tope de 20 000 nodos.

| Clases | BFS (nodos / tiempo) | Costo uniforme (nodos / tiempo) | IDDFS (nodos / tiempo) |
|---:|---|---|---|
| 2 | 2 / 0,0002 s | 2 / 0,0001 s | 3 / <0,0001 s |
| 3 | 22 / 0,0028 s | 22 / 0,006 s | 4 / 0,0001 s |
| 4 | 802 / 0,24 s | 802 / 0,22 s | 5 / 0,0001 s |
| 5 | tope 20 001 / 14,4 s | tope 20 001 / 13,1 s | 6 / 0,0001 s |
| 10 | tope 20 001 / 14,5 s | tope 20 001 / 13,1 s | 11 / 0,0002 s |
| 20 | tope 20 001 / 13,0 s | tope 20 001 / 12,9 s | 21 / 0,0003 s |

Los tiempos dependen del equipo; los conteos de nodos no. Para IDDFS, 21 nodos con 20 clases equivalen a la raíz más una asignación por clase: en estos datos no fue necesario retroceder.

## 7. Análisis

**Por qué BFS y costo uniforme se agotan.** Con costo 1 por clase, costo uniforme expande los estados por costo acumulado, que coincide con la profundidad: en la práctica se comporta como BFS. Ambos deben recorrer casi todos los niveles antes de llegar a la profundidad `d`, y el número de estados crece como `b^d`. En la tabla se ve el salto: de 802 nodos con 4 clases a superar los 20 000 con 5. Ninguna implementación de estos algoritmos puede resolver 20 clases con cientos de opciones por clase; las optimizaciones reducen el trabajo por nodo y el factor de ramificación, pero no cambian el carácter exponencial.

**Por qué IDDFS sí escala aquí.** El problema tiene muchas soluciones y pocas restricciones activas frente al número de recursos; la búsqueda en profundidad avanza asignando clases y casi nunca encuentra un callejón sin salida. Su costo no es `b^d` en la práctica sino del orden de `d` mientras no haya que retroceder. Esto no es una garantía: en instancias muy ajustadas (por ejemplo, profesores o grupos con casi tantas clases como franjas) podría retroceder mucho. Además, IDDFS no mira el costo, así que ignora las preferencias de los profesores.

**Sobre la optimalidad.** Con pasos de costo desigual solo costo uniforme garantiza la solución de menor costo. Es el comportamiento que se observa en la muestra y el que justifica incluir penalizaciones en el modelo.

**Conexión con la búsqueda informada.** El factor limitante de BFS y costo uniforme es que no distinguen estados prometedores. Una heurística admisible, como el número de clases pendientes (cada una cuesta al menos 1), permite que A\* oriente la exploración hacia la meta y mantenga la optimalidad.

## 8. Limitaciones y trabajo futuro

- BFS y costo uniforme solo son prácticos para instancias de pocas clases; el informe los presenta como línea base.
- La simetría de salones asume salones intercambiables (sin capacidad ni tipo). Si se agregan, debe desactivarse con `romper_simetria_salones=False`.
- El costo uniforme con cubetas asume costos enteros.
- El orden de las clases es el del archivo. Ordenar primero las más restringidas (profesores o grupos con más clases) podría reducir el retroceso de IDDFS en instancias ajustadas.
- La penalización considera una sola franja no disponible por profesor, tal como se leen los datos.

## 9. Ejecución

Desde la carpeta raíz del proyecto en Windows:

```powershell
python .\pruebas\prueba_bfs.py
python .\pruebas\prueba_costo_uniforma.py
python .\pruebas\prueba_profundidad_iterativa.py
python .\pruebas\escalabilidad.py
```

Cada script informa el resultado, los nodos explorados, el tiempo y una muestra de las asignaciones, y comprueba que no existan conflictos duros.

## 10. Preguntas y respuestas para la sustentación

### 1. ¿En qué se diferencian los tres algoritmos?

BFS elige por profundidad, costo uniforme por costo acumulado `g(n)` e IDDFS hace búsquedas en profundidad con un límite que aumenta.

### 2. ¿Por qué se fija el orden de las clases?

Cada clase debe programarse exactamente una vez. Asignar siempre la siguiente conserva todas las soluciones y evita caminos redundantes que solo cambian el orden de las mismas decisiones.

### 3. ¿Por qué no hay conjunto de visitados?

Porque con el orden fijo cada estado tiene un único camino: el espacio es un árbol y no hay estados repetidos. Un conjunto de visitados nunca descartaría nada y solo gastaría memoria.

### 4. ¿Por qué BFS no minimiza las preferencias del profesor?

BFS prioriza la profundidad. Todas las soluciones tienen la misma profundidad, así que devuelve la primera que encuentra, sin comparar costos. En la muestra devolvió una clase en franja no disponible.

### 5. ¿Costo uniforme garantiza el menor costo?

Sí, con pasos de costo positivo (aquí al menos 1) y probando la meta al retirar el nodo de la frontera, que es la de menor costo acumulado.

### 6. ¿Cómo implementaron costo uniforme sin `heapq`?

Con un diccionario de cubetas indexado por costo. Los costos son enteros, así que se atiende la cubeta de menor costo y se avanza un contador. Sacar el mínimo cuesta O(1) amortizado, mejor que recorrer toda la lista.

### 7. ¿Por qué IDDFS empieza en el límite `d` y no en 0?

Porque toda solución está a profundidad exactamente `d`. Un límite menor nunca puede contener una meta y obligaría a recorrer todo el árbol hasta ese nivel. Omitirlos no pierde completitud. El parámetro `modo_clasico` ejecuta el IDDFS puro desde 0 para comparar.

### 8. ¿IDDFS garantiza la solución óptima?

Garantiza profundidad mínima, que es igual para todas las soluciones. No garantiza costo mínimo porque no usa `g(n)`.

### 9. ¿Qué significa el conteo de nodos en IDDFS?

Cada llamada recursiva cuenta un nodo. Un mismo estado puede contarse varias veces si se repite al aumentar el límite.

### 10. ¿Por qué BFS y costo uniforme no resuelven 20 clases?

El árbol tiene del orden de `400^20 ≈ 10^52` hojas y ambos algoritmos deben guardar una frontera enorme. Con 20 franjas y 20 salones ya superan los 20 000 nodos con 5 clases. Es una propiedad exponencial del algoritmo, no un error.

### 11. ¿Por qué solo se prueba un salón nuevo en cada paso?

Porque los salones son intercambiables: dos horarios que difieren solo en el nombre de un salón sin usar son equivalentes. Reduce la ramificación sin perder soluciones, siempre que no existan capacidades ni tipos de salón.

### 12. ¿Para qué sirve el prechequeo y el tope de nodos?

El prechequeo descarta casos imposibles de forma inmediata (por ejemplo, un profesor con más clases que franjas). El tope evita que el equipo se quede sin memoria y permite informar que se agotó el límite.

### 13. ¿Qué cambiaría con A\*?

Una heurística admisible, como las clases pendientes, permite priorizar estados cercanos a la meta; así se evita explorar el árbol por niveles y se mantiene la optimalidad.