import os
import sys

ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

from algoritmos.profundidad_iterativa import profundidad_iterativa
from io_datos.lector import (
    cargar_cursos,
    cargar_franjas,
    cargar_profesores,
    cargar_salones,
)
from modelos.clase import Clase
from pruebas.validar_horario import validar_horario


def probar_casos_basicos():
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
        validar_horario(profundidad_iterativa(clases, franjas, salones), clases)

    imposibles = [
        Clase("X1", "Materia 1", "P1", "G1"),
        Clase("X2", "Materia 2", "P1", "G2"),
    ]
    resultado = profundidad_iterativa(
        imposibles, [("Lunes", "07-09")], ["S1", "S2"], prechequeo=False
    )
    assert not resultado["encontro_solucion"]
    assert resultado["solucion"] is None

    limite = profundidad_iterativa(
        [Clase("L1", "Materia", "P1", "G1")],
        [("Lunes", "07-09")],
        ["S1"],
        max_nodos=0,
    )
    assert limite["limite_alcanzado"]
    assert not limite["encontro_solucion"]


def main():
    probar_casos_basicos()

    ruta_archivos = os.path.join(ruta_proyecto, "archivos")
    cursos = cargar_cursos(os.path.join(ruta_archivos, "cursos.txt"))[:3]
    franjas = cargar_franjas(os.path.join(ruta_archivos, "franjas.txt"))[:2]
    salones = cargar_salones(os.path.join(ruta_archivos, "salones.txt"))[:2]
    profesores = cargar_profesores(os.path.join(ruta_archivos, "profesores.txt"))

    resultado = profundidad_iterativa(cursos, franjas, salones, profesores)
    validar_horario(resultado, cursos)
    print(
        f"Profundidad iterativa: solucion para {len(cursos)} clases; "
        f"{resultado['nodos_explorados']} nodos, "
        f"{resultado['tiempo_ejecucion']} s."
    )
    for asignacion in resultado["solucion"]:
        print("  ", asignacion)
    print("Pruebas de profundidad iterativa superadas.")


if __name__ == "__main__":
    main()
