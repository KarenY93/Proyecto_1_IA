import time

try:
    from modelos.estado import Estado
    from algoritmos.nodo import Nodo
    from algoritmos.comun import (
        LimiteDeNodos, armar_resultado, costo_paso,
        generar_sucesores, verificar_factibilidad,
    )
except ImportError:
    from ..modelos.estado import Estado
    from .nodo import Nodo
    from .comun import (
        LimiteDeNodos, armar_resultado, costo_paso,
        generar_sucesores, verificar_factibilidad,
    )


def bfs(clases, franjas, salones, profesores_no_disponibles=None,
        max_nodos=None, romper_simetria_salones=True, prechequeo=True):
    """Busqueda en amplitud: expande todos los estados de un nivel antes del siguiente.

    max_nodos: tope de nodos expandidos; si se alcanza se devuelve
               limite_alcanzado=True en vez de agotar la memoria.
    """
    if profesores_no_disponibles is None:
        profesores_no_disponibles = {}

    inicio = time.perf_counter()
    total_clases = len(clases)

    if prechequeo:
        motivo = verificar_factibilidad(clases, franjas, salones)
        if motivo:
            return armar_resultado(None, None, 0, inicio, motivo=motivo)

    estado_inicial = Estado()
    if total_clases == 0:
        return armar_resultado(estado_inicial, 0, 1, inicio)

    nodos_explorados = 0
    frontera = [Nodo(estado=estado_inicial)]   # cola FIFO
    siguiente = 0                              # indice del frente de la cola
    solucion, costo_solucion, limite = None, None, False

    try:
        while siguiente < len(frontera) and solucion is None:
            actual = frontera[siguiente]
            frontera[siguiente] = None   # libera el nodo ya expandido
            siguiente += 1
            nodos_explorados += 1
            if max_nodos is not None and nodos_explorados > max_nodos:
                raise LimiteDeNodos

            clase = clases[len(actual.estado)]
            es_ultima = len(actual.estado) + 1 == total_clases

            for dia, franja, salon, hijo in generar_sucesores(
                actual.estado, clase, franjas, salones, romper_simetria_salones
            ):
                costo = actual.g + costo_paso(clase, dia, franja, profesores_no_disponibles)
                # En BFS todos los pasos son un nivel: la primera meta GENERADA
                # ya tiene profundidad minima, no hace falta esperar a sacarla.
                if es_ultima:
                    solucion, costo_solucion = hijo, costo
                    break
                # El Estado ya contiene todo el camino (asignaciones), por eso
                # no se guarda 'padre': asi los nodos viejos se pueden liberar.
                frontera.append(Nodo(estado=hijo, accion=(clase.id_curso, dia, franja, salon), g=costo))
    except LimiteDeNodos:
        limite = True

    return armar_resultado(solucion, costo_solucion, nodos_explorados, inicio, limite)