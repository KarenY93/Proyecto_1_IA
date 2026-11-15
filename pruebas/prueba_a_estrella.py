import os
import sys

ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

from algoritmos.a_estrella import a_estrella
from io_datos.lector import (
    cargar_cursos,
    cargar_franjas,
    cargar_profesores,
    cargar_salones,
)
from modelos.clase import Clase
from pruebas.validar_horario import validar_horario


def probar_casos_basicos():
    # 1. Casos solubles minimos
    casos = [
        ([], [], []),
        ([Clase("M1", "Materia", "PM", "GM")], [("Lunes", "07-09")], ["S1"]),
        (
            [Clase("D1", "Materia 1", "P1", "G1"), Clase("D2", "Materia 2", "P1", "G2")],
            [("Lunes", "07-09"), ("Lunes", "09-11")],
            ["S1"],
        ),
    ]
    for clases, franjas, salones in casos:
        validar_horario(a_estrella(clases, franjas, salones), clases)

    # 2. Caso imposible sin prechequeo (recorre arbol)
    imposibles = [
        Clase("X1", "Materia 1", "P1", "G1"),
        Clase("X2", "Materia 2", "P1", "G2"),
    ]
    resultado = a_estrella(
        imposibles, [("Lunes", "07-09")], ["S1", "S2"], prechequeo=False
    )
    assert not resultado["encontro_solucion"]
    assert resultado["solucion"] is None

    # 3. Caso tope de nodos (max_nodos)
    limite = a_estrella(
        [Clase("L1", "Materia", "P1", "G1")],
        [("Lunes", "07-09")],
        ["S1"],
        max_nodos=0,
    )
    assert limite["limite_alcanzado"]
    assert not limite["encontro_solucion"]

    # 4. Caso preferencia blanda: debe elegir la franja disponible para evitar penalizacion
    clase = [Clase("P1", "Calculo", "DOC1", "G1")]
    franjas = [("Lunes", "07-09"), ("Martes", "09-11")]
    resultado = a_estrella(clase, franjas, ["S1"], {"DOC1": franjas[0]})
    validar_horario(resultado, clase)
    assert resultado["solucion"][0][1:3] == franjas[1], "A* debio evitar la franja penalizada"
    assert resultado["costo_solucion"] == 1, "El costo optimo debe ser 1 (sin penalizacion)"


def main():
    probar_casos_basicos()
    print("=" * 60)
    print(" PRUEBA DE BUSQUEDA INFORMADA: ALGORITMO A* ")
    print("=" * 60)
    print("Casos minimo, posible, imposible, limite y preferencia blanda: correctos.")

    ruta_archivos = os.path.join(ruta_proyecto, "archivos")
    cursos = cargar_cursos(os.path.join(ruta_archivos, "cursos.txt"))
    franjas = cargar_franjas(os.path.join(ruta_archivos, "franjas.txt"))
    salones = cargar_salones(os.path.join(ruta_archivos, "salones.txt"))
    profesores = cargar_profesores(os.path.join(ruta_archivos, "profesores.txt"))

    print(f"Total clases a programar: {len(cursos)}")
    print(f"Total franjas disponibles: {len(franjas)}")
    print(f"Total salones disponibles: {len(salones)}")
    print(f"Total profesores leidos: {len(profesores)}")
    print("-" * 60)

    print("Ejecutando A*...")
    resultado = a_estrella(cursos, franjas, salones, profesores, max_nodos=50000)

    print("\nResultados del algoritmo:")
    print(f"- Encontro solucion: {resultado['encontro_solucion']}")
    print(f"- Costo solucion:    {resultado['costo_solucion']}")
    print(f"- Nodos explorados:  {resultado['nodos_explorados']}")
    print(f"- Tiempo ejecucion:  {resultado['tiempo_ejecucion']} s")
    print(f"- Limite alcanzado:  {resultado['limite_alcanzado']}")

    # Validar con la funcion comun
    validar_horario(resultado, cursos)

    mapa_cursos = {c.id_curso: c for c in cursos}
    violaciones_blandas = sum(
        1 for id_curso, dia, franja, _ in resultado["solucion"]
        if profesores.get(mapa_cursos[id_curso].id_profesor) == (dia, franja)
    )
    print(f"- Clases en horario no disponible: {violaciones_blandas}")

    print("\nHorario asignado (primeras 5 clases):")
    print(f"{'Curso':<8} {'Materia':<25} {'Profesor':<8} {'Grupo':<6} {'Dia':<10} {'Franja':<13} {'Salon'}")
    print("-" * 85)
    for id_curso, dia, franja, salon in resultado["solucion"][:5]:
        c = mapa_cursos[id_curso]
        print(f"{id_curso:<8} {c.nombre_materia:<25} {c.id_profesor:<8} {c.grupo:<6} {dia:<10} {franja:<13} {salon}")

    print("\nPrueba de A* superada con exito.")


if __name__ == "__main__":
    main()
