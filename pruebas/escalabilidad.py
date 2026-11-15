"""Mide como crece el trabajo de cada algoritmo al aumentar el numero de clases.

Usa datos sinteticos con el tamano real del problema (20 franjas, 20 salones)
y un tope de nodos para que BFS y costo uniforme terminen y se pueda REPORTAR
cuando se agotan, en lugar de bloquear el equipo.
"""
import os
import sys

ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

from algoritmos.bfs import bfs
from algoritmos.costo_uniforme import costo_uniforme
from algoritmos.profundidad_iterativa import profundidad_iterativa
from modelos.clase import Clase
from pruebas.validar_horario import validar_horario

MAX_NODOS = 20000


def construir_caso(n_clases, n_franjas=20, n_salones=20):
    dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
    horas = ["07-09", "09-11", "11-13", "14-16"]
    franjas = [(d, h) for d in dias for h in horas][:n_franjas]
    salones = [f"S{i + 1}" for i in range(n_salones)]
    clases = [
        Clase(f"C{i + 1}", f"Materia {i + 1}", f"P{i % 5 + 1}", f"G{i % 4 + 1}")
        for i in range(n_clases)
    ]
    return clases, franjas, salones


def ejecutar(nombre, funcion, clases, franjas, salones):
    r = funcion(clases, franjas, salones, {}, max_nodos=MAX_NODOS)
    if r["limite_alcanzado"]:
        estado = f"tope de {MAX_NODOS} nodos"
    else:
        validar_horario(r, clases)
        estado = f"solucion, costo {r['costo_solucion']}"
    print(f"  {nombre:<22} nodos={r['nodos_explorados']:>7}  "
          f"t={r['tiempo_ejecucion']:>7}s  {estado}")


def main():
    for n in (2, 3, 4, 5, 10, 20):
        clases, franjas, salones = construir_caso(n)
        print(f"\n{n} clases, {len(franjas)} franjas, {len(salones)} salones")
        ejecutar("BFS", bfs, clases, franjas, salones)
        ejecutar("Costo uniforme", costo_uniforme, clases, franjas, salones)
        ejecutar("Prof. iterativa", profundidad_iterativa, clases, franjas, salones)


if __name__ == "__main__":
    main()