import time ## lo utilizamos para medir el tiempo de ejecucion del algoritmo con perf_counter
from modelos.estado import Estado
from algoritmos.nodo import Nodo
from algoritmos.comun import (
    LimiteDeNodos,
    armar_resultado,
    costo_paso,
    generar_sucesores,
    verificar_factibilidad,
)


def calcular_heuristica(estado, total_clases):
    # heuristica admisible:cuantas clases faltan por meter al horario
    # como cada clase cuesta minimo 1,jamas va a sobreestimar el costo real
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
    if profesores_no_disponibles is None:
        profesores_no_disponibles = {}

    t_inicio = time.perf_counter()
    total = len(clases)

    # descarte rapido si las dimensiones no dan
    if prechequeo:
        motivo = verificar_factibilidad(clases, franjas, salones)
        if motivo:
            return armar_resultado(None, None, 0, t_inicio, motivo=motivo)

    #el estado inicial es el horario vacion,sino tenemos clases,ya estamos en la meta,costo 0 y 1 nodo
    estado_inicial = Estado()
    if total == 0:
        return armar_resultado(estado_inicial, 0, 1, t_inicio)

    h0 = calcular_heuristica(estado_inicial, total)
    raiz = Nodo(estado_inicial, None, None, 0, h0)

    # TODO: si el profe autoriza librerias meter heapq aca. Con lista nos toca barrido lineal O(N)
    frontera = [raiz]
    nodos_explorados = 0
    solucion = None
    costo_solucion = None
    limite = False

    #el ciclo se repite mientras tengamos nodos por explorar, si la frontera se savia sin meta,no hay solucion.
    try:
        while len(frontera) > 0:
            mejor_idx = 0
            for i in range(1, len(frontera)):
                if frontera[i] < frontera[mejor_idx]:
                    mejor_idx = i

            actual = frontera.pop(mejor_idx)
            nodos_explorados += 1

            if max_nodos is not None and nodos_explorados > max_nodos:
                raise LimiteDeNodos

            if len(actual.estado) == total:
                solucion = actual.estado
                costo_solucion = actual.g
                break

            clase = clases[len(actual.estado)]

            # Generamos los susesores del nodo actual (dia,franja,salon,hijo) y calculamos su costo g y h,para luego agregarlos a la frontera
            for dia, franja, salon, hijo in generar_sucesores(
                actual.estado, clase, franjas, salones, romper_simetria_salones
            ):
                costo_arista = costo_paso(clase, dia, franja, profesores_no_disponibles)
                g_hijo = actual.g + costo_arista
                h_hijo = calcular_heuristica(hijo, total)

                nuevo_nodo = Nodo(
                    hijo,
                    actual,
                    (clase.id_curso, dia, franja, salon),
                    g_hijo,
                    h_hijo,
                )
                frontera.append(nuevo_nodo)

    except LimiteDeNodos:
        limite = True

    return armar_resultado(
        solucion, costo_solucion, nodos_explorados, t_inicio, limite
    )
