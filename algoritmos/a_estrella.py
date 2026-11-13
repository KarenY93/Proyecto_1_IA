import time

try:
    from modelos.estado import Estado
    from algoritmos.nodo import Nodo
except ImportError:
    from ..modelos.estado import Estado
    from .nodo import Nodo


def calcular_heuristica(estado, total_clases):
    # La heuristica calcula cuantas clases faltan por asignar.
    # Es admisible porque cada clase restante costara como minimo 1 unidad en el horario.
    return total_clases - len(estado)


def a_estrella(clases, franjas, salones, profesores_no_disponibles=None):
    """Ejecuta el algoritmo A* para encontrar un horario sin conflictos."""
    if profesores_no_disponibles is None:
        profesores_no_disponibles = {}

    tiempo_inicio = time.time()
    nodos_explorados = 0
    total_clases = len(clases)

    # Estado inicial vacio y nodo raiz
    estado_inicial = Estado()
    h_inicial = calcular_heuristica(estado_inicial, total_clases)
    nodo_raiz = Nodo(estado=estado_inicial, g=0, h=h_inicial)

    # Lista abierta (frontera) y conjunto de estados visitados
    frontera = [nodo_raiz]
    visitados = set()

    solucion_encontrada = None

    while frontera:
        # Busqueda manual del nodo con menor f = g + h
        pos_mejor = 0
        for i in range(1, len(frontera)):
            if frontera[i].f < frontera[pos_mejor].f:
                pos_mejor = i
            elif frontera[i].f == frontera[pos_mejor].f:
                # Si empatan en f, se escoge el que tenga menor h para avanzar a la meta
                if frontera[i].h < frontera[pos_mejor].h:
                    pos_mejor = i

        actual = frontera.pop(pos_mejor)
        nodos_explorados += 1

        # Si ya asignamos todas las clases, llegamos a la meta
        if len(actual.estado) == total_clases:
            solucion_encontrada = actual.estado
            break

        visitados.add(actual.estado.asignaciones)

        # Seleccionar la siguiente clase pendiente por programar
        indice_clase = len(actual.estado)
        siguiente_clase = clases[indice_clase]

        # Generar los sucesores probando cada franja y salon
        for dia, franja in franjas:
            for salon in salones:
                # Comprobamos restricciones duras (profesor, salon o grupo no choquen)
                if actual.estado.puede_asignar(siguiente_clase, dia, franja, salon):
                    hijo_estado = actual.estado.asignar(siguiente_clase, dia, franja, salon)

                    if hijo_estado.asignaciones in visitados:
                        continue

                    # Restriccion blanda: penalizamos si la franja es de no disponibilidad del profesor
                    penalizacion = 0
                    horario_bloqueado = profesores_no_disponibles.get(siguiente_clase.id_profesor)
                    if horario_bloqueado == (dia, franja):
                        penalizacion = 5

                    # Costo acumulado g y valor heuristico h
                    nuevo_g = actual.g + 1 + penalizacion
                    nuevo_h = calcular_heuristica(hijo_estado, total_clases)

                    accion = (siguiente_clase.id_curso, dia, franja, salon)
                    hijo_nodo = Nodo(
                        estado=hijo_estado,
                        padre=actual,
                        accion=accion,
                        g=nuevo_g,
                        h=nuevo_h
                    )

                    frontera.append(hijo_nodo)

    tiempo_fin = time.time()
    tiempo_total = round(tiempo_fin - tiempo_inicio, 4)

    # Estructura del contrato acordado para comunicar con la interfaz
    if solucion_encontrada is not None:
        return {
            "solucion": list(solucion_encontrada.asignaciones),
            "encontro_solucion": True,
            "nodos_explorados": nodos_explorados,
            "tiempo_ejecucion": tiempo_total
        }
    else:
        return {
            "solucion": None,
            "encontro_solucion": False,
            "nodos_explorados": nodos_explorados,
            "tiempo_ejecucion": tiempo_total
        }

