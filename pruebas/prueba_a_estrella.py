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

    imposibles = [
        Clase("X1", "Materia 1", "P1", "G1"),
        Clase("X2", "Materia 2", "P1", "G2"),
    ]
    resultado = a_estrella(
        imposibles, [("Lunes", "07-09")], ["S1", "S2"], prechequeo=False
    )
    assert not resultado["encontro_solucion"]
    assert resultado["solucion"] is None

    limite = a_estrella(
        [Clase("L1", "Materia", "P1", "G1")],
        [("Lunes", "07-09")],
        ["S1"],
        max_nodos=0,
    )
    assert limite["limite_alcanzado"]
    assert not limite["encontro_solucion"]

    clase = [Clase("P1", "Calculo", "DOC1", "G1")]
    franjas = [("Lunes", "07-09"), ("Martes", "09-11")]
    resultado = a_estrella(clase, franjas, ["S1"], {"DOC1": franjas[0]})
    validar_horario(resultado, clase)
    assert resultado["solucion"][0][1:3] == franjas[1]
    assert resultado["costo_solucion"] == 1


def main():
    probar_casos_basicos()

    ruta_archivos = os.path.join(ruta_proyecto, "archivos")
    cursos = cargar_cursos(os.path.join(ruta_archivos, "cursos.txt"))
    franjas = cargar_franjas(os.path.join(ruta_archivos, "franjas.txt"))
    salones = cargar_salones(os.path.join(ruta_archivos, "salones.txt"))
    profesores = cargar_profesores(os.path.join(ruta_archivos, "profesores.txt"))

    resultado = a_estrella(cursos, franjas, salones, profesores, max_nodos=50000)

    print("Resultados de A*:")
    print("Encontro solucion:", resultado["encontro_solucion"])
    print("Costo:", resultado["costo_solucion"])
    print("Nodos explorados:", resultado["nodos_explorados"])
    print("Tiempo:", resultado["tiempo_ejecucion"], "s")

    validar_horario(resultado, cursos)
    print("Prueba completada.")


if __name__ == "__main__":
    main()
