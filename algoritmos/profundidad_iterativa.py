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


def profundidad_iterativa(clases, franjas, salones, profesores_no_disponibles=None,
                          modo_clasico=False, max_nodos=None,
                          romper_simetria_salones=True, prechequeo=True):
    """Busca en profundidad aumentando el límite hasta cubrir todas las clases."""
    if profesores_no_disponibles is None:
        profesores_no_disponibles = {}

    inicio = time.perf_counter()
    total_clases = len(clases)
    if prechequeo:
        motivo = verificar_factibilidad(clases, franjas, salones)
        if motivo:
            return armar_resultado(None, None, 0, inicio, motivo=motivo)

    nodos_explorados = 0

    def buscar(estado, costo, limite):
        nonlocal nodos_explorados
        nodos_explorados += 1
        if max_nodos is not None and nodos_explorados > max_nodos:
            raise LimiteDeNodos

        if len(estado) == total_clases:
            return estado, costo
        if len(estado) == limite:
            return None

        clase = clases[len(estado)]
        for dia, franja, salon, hijo in generar_sucesores(
            estado, clase, franjas, salones, romper_simetria_salones
        ):
            resultado = buscar(
                hijo,
                costo + costo_paso(clase, dia, franja, profesores_no_disponibles),
                limite,
            )
            if resultado is not None:
                return resultado
        return None

    solucion = None
    costo_solucion = None
    limite_alcanzado = False
    primer_limite = 0 if modo_clasico else total_clases

    try:
        for limite in range(primer_limite, total_clases + 1):
            resultado = buscar(Estado(), 0, limite)
            if resultado is not None:
                solucion, costo_solucion = resultado
                break
    except LimiteDeNodos:
        limite_alcanzado = True

    return armar_resultado(
        solucion, costo_solucion, nodos_explorados, inicio, limite_alcanzado
    )
