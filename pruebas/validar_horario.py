def validar_horario(resultado, clases):
    """Comprueba que cada clase este asignada una vez y sin conflictos."""
    assert resultado["encontro_solucion"], "Se esperaba una solucion."

    asignaciones = resultado["solucion"]
    clases_por_id = {clase.id_curso: clase for clase in clases}
    ids_asignados = [asignacion[0] for asignacion in asignaciones]

    assert len(ids_asignados) == len(clases), "Cantidad incorrecta de asignaciones."
    assert len(set(ids_asignados)) == len(ids_asignados), "Una clase aparece mas de una vez."
    assert set(ids_asignados) == set(clases_por_id), "Falta alguna clase."

    salones_ocupados = set()
    profesores_ocupados = set()
    grupos_ocupados = set()

    for id_clase, dia, franja, salon in asignaciones:
        clase = clases_por_id[id_clase]
        llave_salon = (dia, franja, salon)
        llave_profesor = (dia, franja, clase.id_profesor)
        llave_grupo = (dia, franja, clase.grupo)

        assert llave_salon not in salones_ocupados, "Conflicto de salon."
        assert llave_profesor not in profesores_ocupados, "Conflicto de profesor."
        assert llave_grupo not in grupos_ocupados, "Conflicto de grupo."

        salones_ocupados.add(llave_salon)
        profesores_ocupados.add(llave_profesor)
        grupos_ocupados.add(llave_grupo)

    assert resultado["nodos_explorados"] > 0
    assert resultado["tiempo_ejecucion"] >= 0
    return True
