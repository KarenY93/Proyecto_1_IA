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


def costo_uniforme(clases, franjas, salones, profesores_no_disponibles=None,
                   max_nodos=None, romper_simetria_salones=True, prechequeo=True):
    """Busqueda de costo uniforme sin heapq: frontera en 'cubetas' por costo.

    Los costos de paso son enteros (1 o 6), asi que la frontera se guarda como
    un diccionario {costo_acumulado: [nodos]}. Sacar el menor costo es avanzar
    un contador: O(1) amortizado, frente a O(F) de recorrer toda la lista.
    Si algun dia los costos dejan de ser enteros, hay que usar otra estructura.
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
    cubetas = {0: [Nodo(estado=estado_inicial, g=0)]}
    pendientes = 1        # nodos en la frontera
    costo_actual = 0      # cubeta que se esta atendiendo (nunca retrocede)
    solucion, costo_solucion, limite = None, None, False

    try:
        while pendientes and solucion is None:
            while not cubetas.get(costo_actual):
                costo_actual += 1
            actual = cubetas[costo_actual].pop()   # LIFO: entre empates, el mas profundo
            pendientes -= 1
            nodos_explorados += 1
            if max_nodos is not None and nodos_explorados > max_nodos:
                raise LimiteDeNodos

            # Prueba de meta al SACAR el nodo: es lo que garantiza optimalidad.
            if len(actual.estado) == total_clases:
                solucion, costo_solucion = actual.estado, actual.g
                break

            clase = clases[len(actual.estado)]
            for dia, franja, salon, hijo in generar_sucesores(
                actual.estado, clase, franjas, salones, romper_simetria_salones
            ):
                costo = actual.g + costo_paso(clase, dia, franja, profesores_no_disponibles)
                # Atajo valido: ninguna solucion puede costar menos que
                # total_clases (1 por clase). Si un hijo completo llega a ese
                # costo, ya es optimo y no hace falta esperar a sacarlo.
                if len(hijo) == total_clases and costo == total_clases:
                    solucion, costo_solucion = hijo, costo
                    break
                cubetas.setdefault(costo, []).append(
                    Nodo(estado=hijo, accion=(clase.id_curso, dia, franja, salon), g=costo)
                )
                pendientes += 1
    except LimiteDeNodos:
        limite = True

    return armar_resultado(solucion, costo_solucion, nodos_explorados, inicio, limite)