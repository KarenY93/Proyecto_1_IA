# Informe Técnico: Módulo de Búsqueda Informada (A*)
## Sistema de Asignación de Horarios Universitarios

---

## 1. Introducción y Objetivo del Módulo

El objetivo de este módulo es resolver el problema de asignación de horarios académicos universitarios mediante una técnica de **Búsqueda Informada**, específicamente el algoritmo **A\*** implementado desde cero en Python sin librerías externas.

El problema consiste en asignar a cada clase un día, una franja horaria y un salón de clases, garantizando que se cumplan todas las restricciones duras del sistema (sin conflictos de horario, salón, profesor o grupo) y minimizando el costo derivado de restricciones blandas (como los horarios no disponibles de los profesores).

---

## 2. Modelado del Problema

El problema se formaliza como un Problema de Satisfacción de Restricciones (CSP) resuelto mediante exploración en espacios de estados:

### 2.1. Variables
Cada variable representa una sesión de clase a programar:
$$X = \{C_1, C_2, \dots, C_n\}$$
Cada clase contiene:
- `id_curso`: Identificador único de la clase (ej. `C01`).
- `nombre_materia`: Nombre de la asignatura (ej. `Algebra Lineal`).
- `id_profesor`: Identificador del docente asignado (ej. `P01`).
- `grupo`: Grupo de estudiantes (ej. `50`).

### 2.2. Dominio
El dominio de cada variable está compuesto por la combinación de:
$$D = \{ (\text{día}, \text{franja\_horaria}, \text{salón}) \}$$
Para el conjunto de datos de prueba:
- 5 días (Lunes a Viernes) $\times$ 4 franjas horarias por día = 20 franjas horarias.
- 20 salones disponibles.
- Espacio total de asignaciones posibles por clase: $20 \times 20 = 400$ combinaciones.

### 2.3. Restricciones
- **Restricciones Duras (Inviolables):**
  1. *Exclusividad de salón:* Un salón no puede tener más de una clase en la misma franja horaria.
  2. *Exclusividad de profesor:* Un profesor no puede dictar más de una clase en la misma franja horaria.
  3. *Exclusividad de grupo:* Un grupo de estudiantes no puede ver más de una clase en la misma franja horaria.
  4. *Asignación única:* Cada clase debe ser programada exactamente una vez.
- **Restricción Blanda (Optimizables):**
  - Horario de no disponibilidad docente: Si una clase se asigna en la franja que el docente reportó como no disponible, se aplica una penalización en el costo acumulado $g(n)$.

---

## 3. Representación del Estado y del Nodo de Búsqueda

### 3.1. Clase `Estado` (`modelos/estado.py`)
El estado modela una asignación parcial de horarios a lo largo de la búsqueda.
- `asignaciones`: Tupla inmutable con las asignaciones concretadas: `((id_curso, dia, franja, salon), ...)`.
- `_ocupados`: Conjunto inmutable (`frozenset`) con los recursos ocupados:
  - `(dia, franja, "salon", salon)`
  - `(dia, franja, "profesor", id_profesor)`
  - `(dia, franja, "grupo", grupo)`
- **Inmutabilidad:** Cada vez que se programa una clase, el método `asignar()` genera una nueva instancia de `Estado`, garantizando que las ramas del árbol de búsqueda no modifiquen el estado padre.
- **Validación rápida:** El método `puede_asignar(...)` consulta en $O(1)$ el conjunto `_ocupados` para descartar ramas inválidas inmediatamente.

### 3.2. Clase `Nodo` (`algoritmos/nodo.py`)
Representa cada nodo en el árbol de búsqueda generado por A\*:
- `estado`: Estado actual de asignaciones.
- `padre`: Nodo predecesor en el camino.
- `accion`: Asignación realizada para llegar a este nodo `(id_curso, dia, franja, salon)`.
- `g`: Costo acumulado del camino desde la raíz hasta este nodo.
- `h`: Estimación heurística del costo restante hacia la meta.
- `f`: Función de evaluación global $f(n) = g(n) + h(n)$.

---

## 4. Diseño y Justificación de la Heurística

### 4.1. Función de Costo Acumulado $g(n)$
El costo real del camino se define como:
$$g(n) = \text{clases\_asignadas} + \sum \text{penalizaciones\_blandas}$$
- Cada clase programada añade $1$ al costo base de la trayectoria.
- Si una clase se programa en el horario no disponible de su profesor, se añade una penalización de $+5$.
- Esto incentiva al algoritmo a priorizar horarios que respeten la preferencia del profesor.

### 4.2. Función Heurística $h(n)$
La heurística diseñada estima el costo restante para completar el horario:
$$h(n) = \text{total\_clases} - |\text{asignaciones}(n)|$$
Es decir, $h(n)$ es exactamente el número de clases que aún faltan por programar.

### 4.3. Justificación de Admisibilidad y Consistencia
1. **Admisibilidad ($h(n) \le h^*(n)$):**
   - Para alcanzar el estado meta, es obligatorio asignar todas las clases pendientes.
   - Cada clase pendiente que se asigne incrementará el costo real $g$ en al menos $1$ unidad (costo base).
   - Por tanto, el costo real restante $h^*(n) \ge h(n)$, lo cual demuestra que la heurística **nunca sobreestima el costo real**.
   - Al ser admisible, el algoritmo A\* garantiza encontrar una solución de costo óptimo.

2. **Consistencia (Monotonía):**
   - Para cualquier estado $n$ y su sucesor $n'$, el costo de paso es $c(n, a, n') \ge 1$.
   - La diferencia heurística es $h(n) - h(n') = (M - k) - (M - (k + 1)) = 1$.
   - Se cumple la desigualdad triangular: $h(n) \le c(n, a, n') + h(n')$.

### 4.4. Criterio de Desempate (Tie-breaking)
Cuando dos nodos en la lista abierta tienen el mismo valor de evaluación $f(n)$, el algoritmo selecciona el nodo con **menor valor de $h(n)$**:
- Menor $h(n)$ significa que el nodo tiene más clases ya asignadas y está más cerca de la meta.
- Esto dirige la búsqueda hacia la profundidad más prometedora, reduciendo drásticamente la cantidad de nodos explorados.

---

## 5. Implementación del Algoritmo A\* (`algoritmos/a_estrella.py`)

El algoritmo se implementó desde cero utilizando estructuras nativas de Python:

```
A*(clases, franjas, salones, profesores_no_disponibles):
1. Iniciar cronómetro de tiempo.
2. estado_inicial = Estado()
3. nodo_raiz = Nodo(estado=estado_inicial, g=0, h=calcular_heuristica(estado_inicial))
4. frontera = [nodo_raiz]
5. visitados = set()
6. Mientras frontera no esté vacía:
     a. Extraer de la frontera el nodo con menor f (desempate por menor h).
     b. Incrementar contador de nodos_explorados.
     c. Si len(actual.estado) == len(clases):
          Retornar solución encontrada.
     d. Registrar estado actual en visitados.
     e. Seleccionar la siguiente clase pendiente.
     f. Para cada franja y cada salón:
          Si puede_asignar(clase, dia, franja, salon):
             Generar hijo_estado.
             Si hijo_estado ya está en visitados: continuar.
             Calcular penalización blanda si aplica.
             nuevo_g = actual.g + 1 + penalizacion
             nuevo_h = calcular_heuristica(hijo_estado)
             Insertar nuevo Nodo en frontera.
7. Retornar que no se encontró solución.
```

### Contrato de Comunicación
El algoritmo retorna un diccionario con la estructura acordada por el equipo para integrarse directamente con la interfaz gráfica:
```python
{
    "solucion": list(solucion.asignaciones),  # Tuplas (id_curso, dia, franja, salon)
    "encontro_solucion": True,
    "nodos_explorados": nodos_explorados,
    "tiempo_ejecucion": tiempo_total          # En segundos
}
```

---

## 6. Pruebas y Resultados

La validación se llevó a cabo con el script `pruebas/prueba_a_estrella.py` sobre los 20 cursos oficiales ubicados en la carpeta `archivos/`:

### 6.1. Resumen de Ejecución
| Métrica | Valor Obtenido |
| :--- | :--- |
| **Clases a programar** | 20 clases |
| **Franjas horarias** | 20 franjas (5 días $\times$ 4 bloques) |
| **Salones disponibles** | 20 salones |
| **Encontró solución** | **Sí (True)** |
| **Clases asignadas** | **20 de 20 (100 %)** |
| **Nodos explorados** | **21 nodos** |
| **Tiempo de ejecución** | **~0.07 segundos** |
| **Conflictos de salón** | **0** |
| **Conflictos de profesor** | **0** |
| **Conflictos de grupo** | **0** |
| **Violación restricción blanda** | **0 clases en horario no disponible** |

### 6.2. Muestra del Horario Asignado por A\*
| Curso | Materia | Docente | Grupo | Día | Franja | Salón |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **C01** | Álgebra Lineal | P01 | 50 | Lunes | 10:00-12:00 | Salón 101 |
| **C02** | Cálculo Diferencial | P02 | 51 | Lunes | 08:00-10:00 | Salón 101 |
| **C03** | Programación I | P03 | 50 | Lunes | 08:00-10:00 | Salón 102 |
| **C04** | Estructuras de Datos | P04 | 50 | Lunes | 12:00-14:00 | Salón 101 |
| **C05** | Bases de Datos | P05 | 51 | Lunes | 10:00-12:00 | Salón 102 |

Todas las restricciones duras se verificaron mediante aserciones automáticas (`assert`), confirmando la validez completa del horario.

---

## 7. Preguntas y Respuestas para la Sustentación Individual

A continuación se detallan respuestas claras a posibles preguntas que el docente evaluador puede formular durante la sustentación:

#### 1. ¿Cómo funciona la función de evaluación $f(n)$ en su implementación?
> **Respuesta:** $f(n) = g(n) + h(n)$. $g(n)$ mide el costo acumulado desde el inicio (1 punto por clase asignada más 5 puntos si se viola la disponibilidad del profesor), y $h(n)$ es la heurística que cuenta las clases que aún faltan por programar. A\* siempre expande primero el nodo con el menor valor de $f(n)$.

#### 2. ¿Por qué su heurística es admisible y qué pasaría si no lo fuera?
> **Respuesta:** Es admisible porque cada clase que falta por asignar requerirá obligatoriamente al menos una asignación que suma 1 al costo $g$. Por ende, la heurística nunca sobreestima el costo real hacia la meta ($h(n) \le h^*(n)$). Si una heurística no fuera admisible (sobreestimara costos), A\* podría descartar la solución óptima y devolver una solución de peor calidad.

#### 3. ¿Por qué el algoritmo explora tan pocos nodos (21 nodos)?
> **Respuesta:** Porque en cada nivel del árbol fijamos la siguiente clase a asignar en lugar de permutar todas las clases. Además, gracias al desempate por menor $h(n)$ en la frontera y a la comprobación temprana de restricciones en `puede_asignar()`, el algoritmo avanza directo hacia la meta sin necesidad de hacer backtracking masivo.

#### 4. ¿Cómo se evitan los bucles o estados redundantes?
> **Respuesta:** Se mantiene un conjunto `visitados` donde se guardan las asignaciones de cada estado ya expandido. Antes de ingresar un nuevo estado hijo a la frontera, se valida que no haya sido explorado previamente.

#### 5. ¿Qué ocurre si no existe ninguna solución posible para el horario?
> **Respuesta:** El ciclo `while frontera:` continuará hasta agotar todos los estados válidos posibles. Al vaciarse la frontera sin llegar a la meta, el algoritmo retorna `encontro_solucion: False` y `solucion: None`, cumpliendo el contrato de comunicación.

