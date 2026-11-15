import time

try:
    from modelos.estado import Estado
    from algoritmos.nodo import Nodo
    from algoritmos.comun import (
        LimiteDeNodos,
        armar_resultado,
        costo_paso,
        generar_sucesores,
        verificar_factibilidad,
    )
except ImportError:
    from ..modelos.estado import Estado
    from .nodo import Nodo
    from .comun import (
        LimiteDeNodos,
        armar_resultado,
        costo_paso,
        generar_sucesores,
        verificar_factibilidad,
    )


def calcular_heuristica(estado, total_clases):
    # La heuristica estima cuantas clases faltan por programar.
    # Es admisible porque cada clase restante costara como minimo 1 unidad en el horario real.
    return total_clases - len(estado)


def a_estrella(
    clases,
    franjas,
    salones,
    profesores_no_disponibles=None,
    max_nodos=None,
    romper_simetria_salones=True,
    prechequeo=True,
):
    """Busqueda informada A*: expande el nodo con menor evaluacion f(n) = g(n) + h(n).

    - g(n): costo real acumulado (1 por clase + 5 si cae en horario no disponible).
    - h(n): clases restantes por asignar (admisible y consistente).
    - Al usar un orden fijo de clases, el espacio es un arbol puro (sin ciclos ni
      caminos redundantes), por lo que no requiere conjunto de visitados.
    """
    if profesores_no_disponibles is None:
        profesores_no_disponibles = {}

    inicio = time.perf_counter()
    total_clases = len(clases)

    # 1. Prechequeo de factibilidad para detectar casos imposibles de inmediato
    if prechequeo:
        motivo = verificar_factibilidad(clases, franjas, salones)
        if motivo:
            return armar_resultado(None, None, 0, inicio, motivo=motivo)

    estado_inicial = Estado()
    if total_clases == 0:
        return armar_resultado(estado_inicial, 0, 1, inicio)

    h_inicial = calcular_heuristica(estado_inicial, total_clases)
    nodo_raiz = Nodo(estado=estado_inicial, g=0, h=h_inicial)

    frontera = [nodo_raiz]
    nodos_explorados = 0
    solucion = None
    costo_solucion = None
    limite_alcanzado = False

    try:
        while frontera:
            # Buscar el nodo con menor f usando el comparador __lt__ de Nodo
            pos_mejor = 0
            for i in range(1, len(frontera)):
                if frontera[i] < frontera[pos_mejor]:
                    pos_mejor = i

            actual = frontera.pop(pos_mejor)
            nodos_explorados += 1

            if max_nodos is not None and nodos_explorados > max_nodos:
                raise LimiteDeNodos

            # Prueba de meta: se alcanzaron todas las clases
            if len(actual.estado) == total_clases:
                solucion = actual.estado
                costo_solucion = actual.g
                break

            # Siguiente clase segun el orden fijo de asignacion
            clase = clases[len(actual.estado)]

            # Generar sucesores compartidos (rompe simetria de salones y valida restricciones duras)
            for dia, franja, salon, hijo in generar_sucesores(
                actual.estado, clase, franjas, salones, romper_simetria_salones
            ):
                costo_arista = costo_paso(clase, dia, franja, profesores_no_disponibles)
                nuevo_g = actual.g + costo_arista
                nuevo_h = calcular_heuristica(hijo, total_clases)

                hijo_nodo = Nodo(
                    estado=hijo,
                    padre=actual,
                    accion=(clase.id_curso, dia, franja, salon),
                    g=nuevo_g,
                    h=nuevo_h,
                )
                frontera.append(hijo_nodo)

    except LimiteDeNodos:
        limite_alcanzado = True

    return armar_resultado(
        solucion, costo_solucion, nodos_explorados, inicio, limite_alcanzado
    )
