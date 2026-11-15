# Informe Técnico: Módulo de Búsqueda Informada (A*)
## Sistema de Asignación de Horarios Universitarios

---

## 1. Introducción y Objetivo del Módulo

El objetivo de este módulo es resolver el problema de asignación de horarios académicos universitarios mediante una técnica de **Búsqueda Informada**, específicamente el algoritmo **A\*** implementado desde cero en Python sin librerías externas.

El problema consiste en asignar a cada clase un día, una franja horaria y un salón de clases, garantizando que se cumplan todas las restricciones duras del sistema (sin conflictos de horario, salón, profesor o grupo) y minimizando el costo derivado de restricciones blandas (evitando programar docentes en franjas que marcaron como no disponibles).

---

## 2. Modelado Formal del Problema

El problema se formaliza como un Problema de Satisfacción de Restricciones (CSP) resuelto mediante exploración en espacios de estados:

### 2.1. Variables
Cada variable representa una sesión de clase a programar:
$$X = \{C_1, C_2, \dots, C_n\}$$
Donde cada clase contiene:
- `id_curso`: Identificador único de la clase (ej. `C01`).
- `nombre_materia`: Nombre de la asignatura (ej. `Algebra Lineal`).
- `id_profesor`: Identificador del docente asignado (ej. `P01`).
- `grupo`: Grupo de estudiantes (ej. `50`).

### 2.2. Dominio de las Variables
El dominio está compuesto por el conjunto de ternas posibles:
$$D = \{ (\text{día}, \text{franja\_horaria}, \text{salón}) \}$$
Para el dataset del proyecto:
- 5 días $\times$ 4 franjas por día = 20 franjas horarias.
- 20 salones disponibles.
- Espacio total de asignaciones posibles por clase: $20 \times 20 = 400$ combinaciones.

### 2.3. Restricciones
- **Restricciones Duras (Inviolables):**
  1. *Exclusividad de salón:* Un salón no puede tener más de una clase en el mismo día y franja.
  2. *Exclusividad de profesor:* Un profesor no puede dictar más de una clase en el mismo día y franja.
  3. *Exclusividad de grupo:* Un grupo de estudiantes no puede ver más de una clase en el mismo día y franja.
  4. *Asignación única:* Cada clase debe ser programada exactamente una vez.
- **Restricción Blanda (Optimizables):**
  - Horario no disponible del docente: Si una clase se asigna en la franja que el docente reportó como no disponible, se aplica una penalización en el costo acumulado $g(n)$ ($+5$).

---

## 3. Representación del Estado, del Nodo y del Espacio de Búsqueda

### 3.1. Estado Inmutable (`modelos/estado.py`)
Modela una asignación parcial del horario:
- `asignaciones`: Tupla con las asignaciones hechas: `((id_curso, dia, franja, salon), ...)`.
- `_ocupados`: Conjunto inmutable (`frozenset`) con los recursos ocupados:
  - `(dia, franja, "salon", salon)`
  - `(dia, franja, "profesor", id_profesor)`
  - `(dia, franja, "grupo", grupo)`
- **Verificación rápida por franja:** Se verifica primero si profesor y grupo están libres en la franja (`puede_en_franja`). Si alguno está ocupado, se descartan todos los salones de inmediato sin evaluarlos uno por uno.

### 3.2. Estructura del Nodo (`algoritmos/nodo.py`)
Cada nodo del árbol de búsqueda contiene:
- `estado`: Estado parcial del horario.
- `padre`: Referencia al nodo predecesor.
- `accion`: Asignación realizada `(id_curso, dia, franja, salon)`.
- `g`: Costo real acumulado desde la raíz.
- `h`: Estimación heurística del costo restante hacia la meta.
- `f`: Función de evaluación global $f(n) = g(n) + h(n)$.
- `__lt__(otro)`: Comparador de prioridad. Si dos nodos empatan en $f(n)$, desempata priorizando el nodo con **menor heurística $h(n)$** (más avanzado en profundidad).

### 3.3. Estructura de Árbol (Por qué no se necesita conjunto de visitados)
Al fijar el orden de asignación de las clases (`clases[len(estado)]`), a profundidad $0$ siempre se asigna la primera clase, a profundidad $1$ la segunda, y así sucesivamente.
- **Consecuencia teórica:** Cada estado se alcanza por un único camino; es imposible llegar al mismo estado por rutas alternas.
- El espacio de estados es estrictamente un **árbol**, no un grafo con ciclos.
- Por ello, no se requiere un conjunto `visitados` (tabla de cerrados), ahorrando memoria y tiempo de cálculo de hash en cada iteración.

---

## 4. Diseño y Justificación de la Heurística

### 4.1. Función de Costo Acumulado $g(n)$
$$g(n) = \text{clases\_asignadas} + \sum \text{penalizaciones\_blandas}$$
- Cada clase programada añade $1$ al costo base del camino.
- Si una clase se programa en el horario no disponible de su profesor, se añade una penalización de $+5$.

### 4.2. Función Heurística $h(n)$
$$h(n) = \text{total\_clases} - |\text{asignaciones}(n)|$$
Estima la cantidad de clases que aún faltan por programar.

### 4.3. Justificación de Admisibilidad y Consistencia
1. **Admisibilidad ($h(n) \le h^*(n)$):**
   - Para llegar a la meta es obligatorio programar todas las clases restantes.
   - Cada clase restante agregará como mínimo $1$ unidad al costo real $g$.
   - Por tanto, $h^*(n) \ge h(n)$, garantizando que la heurística **nunca sobreestima** el costo real.
2. **Consistencia (Monotonía):**
   - Para cualquier transición $n \to n'$, el costo de paso es $c(n, a, n') \ge 1$.
   - La diferencia heurística es $h(n) - h(n') = 1$.
   - Se cumple la desigualdad triangular: $h(n) \le c(n, a, n') + h(n')$.

### 4.4. Comportamiento de $f(n)$ y Criterio de Desempate
- **Sin penalizaciones:** $g(n) = k$ y $h(n) = M - k$, por lo que $f(n) = k + (M - k) = M$ (constante para todos los nodos). En este escenario, el desempate por menor $h(n)$ en `Nodo.__lt__` hace que A\* avance en profundidad directa hacia la meta (DFS informada).
- **Con penalizaciones:** Si un nodo asigna una clase en una franja bloqueada, su $g(n)$ sube en $+5$, por lo que $f(n) = M + 5$. A\* pospone automáticamente ese nodo y prefiere ramas limpias sin penalización.

---

## 5. Implementación del Algoritmo A\* (`algoritmos/a_estrella.py`)

Se implementó desde cero reutilizando la infraestructura compartida del proyecto (`algoritmos/comun.py`):

```
A*(clases, franjas, salones, profesores_no_disponibles, max_nodos, romper_simetria_salones, prechequeo):
1. Iniciar cronómetro de tiempo (time.perf_counter).
2. Si prechequeo está activo:
     motivo = verificar_factibilidad(clases, franjas, salones)
     Si hay incoherencia (ej. más clases que franjas): retornar sin buscar.
3. Crear nodo raíz con Estado vacío, g=0 y h=calcular_heuristica(Estado()).
4. frontera = [nodo_raiz]
5. Mientras frontera no esté vacía:
     a. Encontrar el mejor nodo usando frontera[i] < frontera[pos_mejor] (ejecuta Nodo.__lt__).
     b. actual = frontera.pop(pos_mejor)
     c. Incrementar nodos_explorados.
     d. Si nodos_explorados > max_nodos: abortar por límite alcanzado.
     e. Si len(actual.estado) == total_clases: retornar solución y costo_solucion.
     f. clase = clases[len(actual.estado)]
     g. Para cada (dia, franja, salon, hijo) en generar_sucesores(...):
          nuevo_g = actual.g + costo_paso(...)
          nuevo_h = calcular_heuristica(hijo, total_clases)
          Insertar nuevo Nodo en la frontera.
6. Retornar que no se encontró solución.
```

### Contrato Unificado de Comunicación
Retorna el diccionario idéntico al de los algoritmos no informados mediante `armar_resultado`:
```python
{
    "solucion": list(solucion.asignaciones),  # Tuplas (id_curso, dia, franja, salon)
    "encontro_solucion": True,
    "costo_solucion": costo_solucion,         # Costo total óptimo (ej. 20)
    "nodos_explorados": nodos_explorados,
    "tiempo_ejecucion": round(tiempo, 4),     # En segundos
    "limite_alcanzado": limite_alcanzado,     # True si alcanzó max_nodos
    "motivo": motivo                          # Motivo si falló el prechequeo
}
```

---

## 6. Pruebas y Resultados Experimentales

La suite de pruebas en [prueba_a_estrella.py](file:///c:/Users/ASUS/Documents/UNIprogramacion/Python/IA/Proyecto_1_IA/pruebas/prueba_a_estrella.py) evalúa los casos unitarios y el dataset completo de 20 clases:

### 6.1. Casos Unitarios
1. **Caso mínimo:** Programación de 1 clase en 1 franja y 1 salón $\to$ Éxito.
2. **Caso soluble:** 2 clases del mismo profesor programadas en franjas distintas $\to$ Éxito.
3. **Caso sin solución:** 2 clases del mismo profesor con 1 sola franja disponible $\to$ Devuelve `encontro_solucion: False` y `solucion: None`.
4. **Tope de nodos:** Ejecución con `max_nodos=0` $\to$ Devuelve `limite_alcanzado: True`.
5. **Preferencia blanda:** Profesor con una franja bloqueada y otra libre $\to$ A\* escoge la franja libre (costo 1 vs costo 6).

### 6.2. Resultados con las 20 Clases del Proyecto
| Métrica | Algoritmo A\* |
| :--- | :--- |
| **Clases programadas** | **20 de 20 (100 %)** |
| **Costo de la solución** | **20 (Óptimo, sin penalizaciones)** |
| **Nodos explorados** | **21 nodos** |
| **Tiempo de ejecución** | **~0.0045 segundos** |
| **Límite alcanzado** | **False** |
| **Conflictos de salón, profesor o grupo** | **0 (Validados por `validar_horario`)** |
| **Clases en horario no disponible** | **0** |

---

## 7. Preguntas y Respuestas Clave para la Sustentación Individual

#### 1. ¿Por qué A\* exploró solo 21 nodos con 20 clases?
> **Respuesta:** En cada nivel del árbol se asigna una clase fija. Dado que hay suficientes franjas y salones libres, la heurística y la validación temprana de restricciones guían la búsqueda directamente hacia la meta sin retrocesos. 21 nodos corresponden exactamente a la raíz más una asignación por cada una de las 20 clases.

#### 2. ¿Por qué no se utilizó un conjunto de estados visitados en A\*?
> **Respuesta:** En problemas CSP donde las variables se asignan en un orden estricto predeterminado, cada estado parcial tiene un único camino posible de generación. El espacio de estados resultante es estrictamente un árbol sin caminos convergentes ni ciclos. Almacenar estados visitados solo consumiría memoria y tiempo de hashing sin descartar ningún nodo repetido.

#### 3. ¿Cómo funciona la frontera sin usar `heapq` y cómo se usa `Nodo.__lt__`?
> **Respuesta:** Para respetar la restricción de no usar bibliotecas externas, la frontera es una lista nativa. Para extraer el mejor nodo, se busca la posición mínima mediante `if frontera[i] < frontera[pos_mejor]:`, lo que invoca automáticamente el método especial `__lt__` de la clase `Nodo`. Este método compara los valores de $f(n)$ y desempata por menor $h(n)$.

#### 4. ¿Qué ocurre con la función de evaluación $f(n)$ si no hay penalizaciones blandas?
> **Respuesta:** $f(n) = g(n) + h(n) = k + (M - k) = M$ (una constante igual al total de clases). Todos los nodos tienen el mismo valor de $f(n)$. En ese caso, el criterio de desempate por menor $h(n)$ hace que A\* se comporte como una búsqueda en profundidad (DFS). Sin embargo, cuando se consideran las penalizaciones blandas, $g(n)$ penaliza los horarios bloqueados, haciendo que $f(n)$ distinga y evite los caminos de mayor costo.

#### 5. ¿Cómo se integra A\* con la interfaz gráfica?
> **Respuesta:** A\* utiliza la función `armar_resultado` de `comun.py`, devolviendo exactamente las mismas claves que los demás algoritmos (`solucion`, `costo_solucion`, `nodos_explorados`, `tiempo_ejecucion`, etc.). Además acepta el parámetro `max_nodos`, permitiendo que la interfaz gráfica controle el tiempo de ejecución en hilos secundarios sin bloqueos.
