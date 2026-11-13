import os
import sys

ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

from io_datos.lector import (
    cargar_cursos,
    cargar_franjas,
    cargar_salones,
    cargar_profesores,
)
from algoritmos.bfs import bfs
from modelos.clase import Clase
from pruebas.validar_horario import validar_horario


def probar_casos_basicos():
    caso_minimo = [Clase("M1", "Materia", "PM", "GM")]
    resultado_minimo = bfs(caso_minimo, [("Lunes", "07-09")], ["S1"])
    validar_horario(resultado_minimo, caso_minimo)

    caso_dos_franjas = [
        Clase("D1", "Materia 1", "P1", "G1"),
        Clase("D2", "Materia 2", "P1", "G2"),
    ]
    franjas = [("Lunes", "07-09"), ("Lunes", "09-11")]
    resultado_dos_franjas = bfs(caso_dos_franjas, franjas, ["S1"])
    validar_horario(resultado_dos_franjas, caso_dos_franjas)

    caso_imposible = [
        Clase("X1", "Materia 1", "P1", "G1"),
        Clase("X2", "Materia 2", "P1", "G2"),
    ]
    resultado_imposible = bfs(
        caso_imposible, [("Lunes", "07-09")], ["S1", "S2"], prechequeo=False
    )
    assert not resultado_imposible["encontro_solucion"]
    assert resultado_imposible["solucion"] is None


def main():
    print("=" * 60)
    print(" PRUEBA DE BUSQUEDA NO INFORMADA: BFS ")
    print("=" * 60)
    probar_casos_basicos()
    print("Casos minimo, posible e imposible: correctos.")

    ruta_archivos = os.path.join(ruta_proyecto, "archivos")
    todos_cursos = cargar_cursos(os.path.join(ruta_archivos, "cursos.txt"))
    todas_franjas = cargar_franjas(os.path.join(ruta_archivos, "franjas.txt"))
    todos_salones = cargar_salones(os.path.join(ruta_archivos, "salones.txt"))
    profesores = cargar_profesores(os.path.join(ruta_archivos, "profesores.txt"))

    cursos = todos_cursos[:3]
    franjas = todas_franjas[:2]
    salones = todos_salones[:2]

    print(f"Clases leidas: {len(todos_cursos)}")
    print(f"Franjas leidas: {len(todas_franjas)}")
    print(f"Salones leidos: {len(todos_salones)}")
    print(f"Total profesores leidos: {len(profesores)}")
    print(
        f"Muestra usada: {len(cursos)} clases, "
        f"{len(franjas)} franjas y {len(salones)} salones"
    )
    print("-" * 60)

    print("Ejecutando BFS...")
    resultado = bfs(cursos, franjas, salones, profesores)
    print("\nResultados del algoritmo:")
    print(f"- Encontro solucion: {resultado['encontro_solucion']}")
    print(f"- Nodos explorados:  {resultado['nodos_explorados']}")
    print(f"- Tiempo ejecucion:  {resultado['tiempo_ejecucion']} s")

    if not resultado["encontro_solucion"]:
        print("\nERROR: No se pudo encontrar una asignacion valida.")
        return

    solucion = resultado["solucion"]
    print(f"- Clases asignadas:  {len(solucion)} de {len(cursos)}")
    print("\nVerificando restricciones del problema...")

    mapa_cursos = {curso.id_curso: curso for curso in cursos}
    salones_ocupados = set()
    profesores_ocupados = set()
    grupos_ocupados = set()
    clases_asignadas = set()
    conflictos = 0
    violaciones_blandas = 0

    for id_curso, dia, franja, salon in solucion:
        curso = mapa_cursos[id_curso]
        if id_curso in clases_asignadas:
            print(f"Conflicto: la clase {id_curso} esta repetida.")
            conflictos += 1
        clases_asignadas.add(id_curso)

        llave_salon = (dia, franja, salon)
        if llave_salon in salones_ocupados:
            print(f"Conflicto de salon: {salon} en {dia} {franja}")
            conflictos += 1
        salones_ocupados.add(llave_salon)

        llave_profesor = (dia, franja, curso.id_profesor)
        if llave_profesor in profesores_ocupados:
            print(f"Conflicto de profesor: {curso.id_profesor} en {dia} {franja}")
            conflictos += 1
        profesores_ocupados.add(llave_profesor)

        llave_grupo = (dia, franja, curso.grupo)
        if llave_grupo in grupos_ocupados:
            print(f"Conflicto de grupo: {curso.grupo} en {dia} {franja}")
            conflictos += 1
        grupos_ocupados.add(llave_grupo)

        if profesores.get(curso.id_profesor) == (dia, franja):
            violaciones_blandas += 1

    assert clases_asignadas == set(mapa_cursos), "No se asignaron todas las clases"
    assert conflictos == 0, f"Se encontraron {conflictos} conflictos en el horario"

    print("-> Restricciones duras: 0 conflictos detectados (Exito)")
    print(f"-> Clases en horario no disponible: {violaciones_blandas}")
    print("\nHorario asignado (primeras 5 clases):")
    print(f"{'Curso':<8} {'Materia':<25} {'Profesor':<8} {'Grupo':<6} {'Dia':<10} {'Franja':<13} {'Salon'}")
    print("-" * 85)
    for id_curso, dia, franja, salon in solucion[:5]:
        curso = mapa_cursos[id_curso]
        print(f"{id_curso:<8} {curso.nombre_materia:<25} {curso.id_profesor:<8} {curso.grupo:<6} {dia:<10} {franja:<13} {salon}")

    print("\nPrueba de BFS superada con exito.")


if __name__ == "__main__":
    main()