"""Funciones compartidas por BFS, costo uniforme y profundidad iterativa.

Centralizar aqui la generacion de sucesores, el costo de un paso y el formato
del resultado evita repetir codigo y garantiza que los tres algoritmos
exploren exactamente el mismo espacio de estados.
"""
import time


class LimiteDeNodos(Exception):
    """Se alcanzo el maximo de nodos permitido (protege memoria y tiempo)."""


def costo_paso(clase, dia, franja, profesores_no_disponibles):
    """1 por clase programada, +5 si cae en la franja no disponible del profesor."""
    costo = 1
    if profesores_no_disponibles.get(clase.id_profesor) == (dia, franja):
        costo += 5
    return costo


def _salones_a_probar(estado, salones, romper_simetria):
    """Rompe la simetria entre salones intercambiables.

    Si los salones no tienen capacidad ni tipo, dos horarios que solo difieren
    en el NOMBRE de un salon sin usar son equivalentes. Basta probar los
    salones ya usados y el primer salon nunca usado. Solo es valido mientras
    todos los salones sean intercambiables.
    """
    if not romper_simetria:
        return salones
    usados = {asignacion[3] for asignacion in estado.asignaciones}
    candidatos = []
    nuevo_agregado = False
    for salon in salones:
        if salon in usados:
            candidatos.append(salon)
        elif not nuevo_agregado:
            candidatos.append(salon)
            nuevo_agregado = True
    return candidatos


def generar_sucesores(estado, clase, franjas, salones, romper_simetria=True):
    """Genera (dia, franja, salon, estado_hijo) para la clase dada."""
    if estado.esta_asignada(clase.id_curso):
        return
    candidatos = _salones_a_probar(estado, salones, romper_simetria)
    for dia, franja in franjas:
        # Profesor y grupo dependen solo de la franja: se revisan una vez
        # y asi se descartan todos los salones de golpe.
        if not estado.puede_en_franja(clase, dia, franja):
            continue
        for salon in candidatos:
            if estado.salon_libre(dia, franja, salon):
                hijo = estado.asignar(clase, dia, franja, salon, verificar=False)
                yield dia, franja, salon, hijo


def verificar_factibilidad(clases, franjas, salones):
    """Condiciones NECESARIAS para que exista horario. Devuelve el motivo o None.

    Si falla alguna, no hace falta buscar: el problema no tiene solucion.
    """
    n_franjas = len(set(franjas))
    if len(clases) > n_franjas * len(set(salones)):
        return "hay mas clases que pares (franja, salon)"
    por_profesor, por_grupo = {}, {}
    for clase in clases:
        por_profesor[clase.id_profesor] = por_profesor.get(clase.id_profesor, 0) + 1
        por_grupo[clase.grupo] = por_grupo.get(clase.grupo, 0) + 1
    for id_profesor, cantidad in por_profesor.items():
        if cantidad > n_franjas:
            return f"el profesor {id_profesor} tiene mas clases que franjas"
    for grupo, cantidad in por_grupo.items():
        if cantidad > n_franjas:
            return f"el grupo {grupo} tiene mas clases que franjas"
    return None


def armar_resultado(solucion, costo, nodos, inicio, limite_alcanzado=False, motivo=None):
    """Diccionario de salida comun a los tres algoritmos."""
    return {
        "solucion": list(solucion.asignaciones) if solucion is not None else None,
        "encontro_solucion": solucion is not None,
        "costo_solucion": costo if solucion is not None else None,
        "nodos_explorados": nodos,
        "tiempo_ejecucion": round(time.perf_counter() - inicio, 4),
        "limite_alcanzado": limite_alcanzado,
        "motivo": motivo,
    }