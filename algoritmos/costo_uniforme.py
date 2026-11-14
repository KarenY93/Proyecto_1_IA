import time

try:
    from modelos.estado import Estado
    from algoritmos.comun import (
        LimiteDeNodos,
        armar_resultado,
        costo_paso,
        generar_sucesores,
        verificar_factibilidad,
    )
except ImportError:
    from ..modelos.estado import Estado
    from .comun import (
        LimiteDeNodos,
        armar_resultado,
        costo_paso,
        generar_sucesores,
        verificar_factibilidad,
    )


def costo_uniforme(clases, franjas, salones, profesores_no_disponibles=None,
                   max_nodos=None, romper_simetria_salones=True, prechequeo=True):
    """Busca primero los horarios parciales de menor costo acumulado."""
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

    # Los costos son enteros, así que cada lista guarda nodos con el mismo costo.
    frontera = {0: [(estado_inicial, 0)]}
    nodos_pendientes = 1
    costo_actual = 0
    nodos_explorados = 0
    solucion = None
    costo_solucion = None
    limite_alcanzado = False

    try:
        while nodos_pendientes:
            while not frontera.get(costo_actual):
                costo_actual += 1

            estado, costo = frontera[costo_actual].pop()
            nodos_pendientes -= 1
            nodos_explorados += 1
            if max_nodos is not None and nodos_explorados > max_nodos:
                raise LimiteDeNodos

            if len(estado) == total_clases:
                solucion = estado
                costo_solucion = costo
                break

            clase = clases[len(estado)]
            for dia, franja, salon, hijo in generar_sucesores(
                estado, clase, franjas, salones, romper_simetria_salones
            ):
                nuevo_costo = costo + costo_paso(
                    clase, dia, franja, profesores_no_disponibles
                )
                if len(hijo) == total_clases and nuevo_costo == total_clases:
                    solucion = hijo
                    costo_solucion = nuevo_costo
                    break
                frontera.setdefault(nuevo_costo, []).append((hijo, nuevo_costo))
                nodos_pendientes += 1
            if solucion is not None:
                break
    except LimiteDeNodos:
        limite_alcanzado = True

    return armar_resultado(
        solucion, costo_solucion, nodos_explorados, inicio, limite_alcanzado
    )
