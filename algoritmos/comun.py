import time


class LimiteDeNodos(Exception):
    # excepcion propia para cortar la busqueda cuando se supera max_nodos y no colgar la UI
    pass


def costo_paso(clase, dia, franja, profesores_no_disponibles):
    # base 1 por clase, penalizamos con +5 si metemos al profesor en su horario bloqueado
    costo = 1
    if profesores_no_disponibles.get(clase.id_profesor) == (dia, franja):
        costo += 5
    return costo


def _salones_a_probar(estado, salones, romper_simetria):
    # si los salones son todos iguales,probar todos los vacios genera ramas espejo
    # basta con probar los que ya tienen alguna clase asignada + un salon nuevo disponible
    if not romper_simetria:
        return salones

    usados = {asignacion[3] for asignacion in estado.asignaciones}
    candidatos = [s for s in salones if s in usados]
    for s in salones:
        if s not in usados:
            candidatos.append(s)
            break
    return candidatos

# esto define la creacion/expansion de nodos
def generar_sucesores(estado, clase, franjas, salones, romper_simetria=True):
    if estado.esta_asignada(clase.id_curso):
        return
    candidatos = _salones_a_probar(estado, salones, romper_simetria)
    for dia, franja in franjas:
        # si el profesor o grupo ya estan ocupados en esta franja, ni miramos los salones
        if not estado.puede_en_franja(clase, dia, franja):
            continue
        for salon in candidatos:
            if estado.salon_libre(dia, franja, salon):
                hijo = estado.asignar(clase, dia, franja, salon, verificar=False)
                yield dia, franja, salon, hijo


def verificar_factibilidad(clases, franjas, salones):
    # validaciones basicas para descartar casos imposibles antes de gastar memoria en el arbol
    n_franjas = len(set(franjas))
    if len(clases) > n_franjas * len(set(salones)):
        return "hay mas clases que pares (franja, salon)"
    por_profesor, por_grupo = {}, {}
    for c in clases:
        por_profesor[c.id_profesor] = por_profesor.get(c.id_profesor, 0) + 1
        por_grupo[c.grupo] = por_grupo.get(c.grupo, 0) + 1
    for id_prof, cantidad in por_profesor.items():
        if cantidad > n_franjas:
            return f"el profesor {id_prof} tiene mas clases que franjas"
    for grp, cantidad in por_grupo.items():
        if cantidad > n_franjas:
            return f"el grupo {grp} tiene mas clases que franjas"
    return None


def armar_resultado(solucion, costo, nodos, inicio, limite_alcanzado=False, motivo=None):
    return {
        "solucion": list(solucion.asignaciones) if solucion is not None else None,
        "encontro_solucion": solucion is not None,
        "costo_solucion": costo if solucion is not None else None,
        "nodos_explorados": nodos,
        "tiempo_ejecucion": round(time.perf_counter() - inicio, 4),
        "limite_alcanzado": limite_alcanzado,
        "motivo": motivo,
    }
