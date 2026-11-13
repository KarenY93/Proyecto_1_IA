import os
import sys

# Asegurar que se puedan importar modulos desde la raiz del proyecto
ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

from io_datos.lector import (
    cargar_cursos,
    cargar_franjas,
    cargar_salones,
    cargar_profesores,
)
from algoritmos.a_estrella import a_estrella


def main():
    print("=" * 60)
    print(" PRUEBA DE BUSQUEDA INFORMADA: ALGORITMO A* ")
    print("=" * 60)

    # 1. Cargar datos desde los archivos TXT
    ruta_archivos = os.path.join(ruta_proyecto, "archivos")
    ruta_cursos = os.path.join(ruta_archivos, "cursos.txt")
    ruta_franjas = os.path.join(ruta_archivos, "franjas.txt")
    ruta_salones = os.path.join(ruta_archivos, "salones.txt")
    ruta_profesores = os.path.join(ruta_archivos, "profesores.txt")

    cursos = cargar_cursos(ruta_cursos)
    franjas = cargar_franjas(ruta_franjas)
    salones = cargar_salones(ruta_salones)
    profesores = cargar_profesores(ruta_profesores)

    print(f"Total clases a programar: {len(cursos)}")
    print(f"Total franjas disponibles: {len(franjas)}")
    print(f"Total salones disponibles: {len(salones)}")
    print(f"Total profesores leidos: {len(profesores)}")
    print("-" * 60)

    # 2. Ejecutar algoritmo A*
    print("Ejecutando A*...")
    resultado = a_estrella(cursos, franjas, salones, profesores)

    # 3. Mostrar resultados y estadisticas
    print("\nResultados del algoritmo:")
    print(f"- Encontro solucion: {resultado['encontro_solucion']}")
    print(f"- Nodos explorados:  {resultado['nodos_explorados']}")
    print(f"- Tiempo ejecucion:  {resultado['tiempo_ejecucion']} s")

    if not resultado["encontro_solucion"]:
        print("\nERROR: No se pudo encontrar una asignacion valida.")
        return

    solucion = resultado["solucion"]
    print(f"- Clases asignadas:  {len(solucion)} de {len(cursos)}")

    # 4. Validacion estricta de restricciones duras
    print("\nVerificando restricciones del problema...")

    salones_ocupados = set()
    profesores_ocupados = set()
    grupos_ocupados = set()
    clases_asignadas = set()

    mapa_cursos = {c.id_curso: c for c in cursos}
    conflictos = 0
    violaciones_blandas = 0

    for id_curso, dia, franja, salon in solucion:
        curso = mapa_cursos[id_curso]

        # Validar clase unica
        if id_curso in clases_asignadas:
            print(f"Conflicto: la clase {id_curso} esta repetida.")
            conflictos += 1
        clases_asignadas.add(id_curso)

        # Validar salon libre
        llave_salon = (dia, franja, salon)
        if llave_salon in salones_ocupados:
            print(f"Conflicto de salon: {salon} en {dia} {franja}")
            conflictos += 1
        salones_ocupados.add(llave_salon)

        # Validar profesor libre
        llave_prof = (dia, franja, curso.id_profesor)
        if llave_prof in profesores_ocupados:
            print(f"Conflicto de profesor: {curso.id_profesor} en {dia} {franja}")
            conflictos += 1
        profesores_ocupados.add(llave_prof)

        # Validar grupo de estudiantes libre
        llave_grupo = (dia, franja, curso.grupo)
        if llave_grupo in grupos_ocupados:
            print(f"Conflicto de grupo: {curso.grupo} en {dia} {franja}")
            conflictos += 1
        grupos_ocupados.add(llave_grupo)

        # Contar restriccion blanda
        if profesores.get(curso.id_profesor) == (dia, franja):
            violaciones_blandas += 1

    # Comprobaciones con assert
    assert len(clases_asignadas) == len(cursos), "No se asignaron todas las clases"
    assert conflictos == 0, f"Se encontraron {conflictos} conflictos en el horario"

    print("-> Restricciones duras: 0 conflictos detectados (Exito)")
    print(f"-> Clases en horario no disponible de profesores: {violaciones_blandas}")

    # 5. Vista previa de los horarios generados
    print("\nHorario asignado (primeras 5 clases):")
    print(f"{'Curso':<8} {'Materia':<25} {'Profesor':<8} {'Grupo':<6} {'Dia':<10} {'Franja':<13} {'Salon'}")
    print("-" * 85)
    for id_curso, dia, franja, salon in solucion[:5]:
        c = mapa_cursos[id_curso]
        print(f"{id_curso:<8} {c.nombre_materia:<25} {c.id_profesor:<8} {c.grupo:<6} {dia:<10} {franja:<13} {salon}")

    print("\nPrueba de A* superada con exito.")


if __name__ == "__main__":
    main()

