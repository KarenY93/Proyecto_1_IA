import os
import sys

ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

from modelos.clase import Clase
from algoritmos.a_estrella import a_estrella
from io_datos.lector import (
    cargar_cursos,
    cargar_franjas,
    cargar_salones,
    cargar_profesores,
)
from pruebas.validar_horario import validar_horario


def test_caso_vacio():
    print("1. Probando caso vacio (0 clases)...")
    r = a_estrella([], [], [])
    assert r["encontro_solucion"] is True
    assert r["solucion"] == []
    assert r["costo_solucion"] == 0
    assert r["nodos_explorados"] == 1
    print("   -> OK: Solucion vacia correcta, costo 0.")


def test_caso_minimo():
    print("2. Probando caso minimo (1 clase, 1 franja, 1 salon)...")
    clases = [Clase("C1", "Calculo", "P1", "G1")]
    franjas = [("Lunes", "08:00-10:00")]
    salones = ["S101"]
    r = a_estrella(clases, franjas, salones)
    validar_horario(r, clases)
    assert r["costo_solucion"] == 1
    assert r["nodos_explorados"] == 2
    print("   -> OK: Asignacion unica correcta, costo 1, 2 nodos explorados.")


def test_conflicto_profesor():
    print("3. Probando conflicto de profesor (2 clases mismo profesor, 2 franjas, 1 salon)...")
    clases = [
        Clase("C1", "Algebra", "P1", "G1"),
        Clase("C2", "Calculo", "P1", "G2"),
    ]
    franjas = [("Lunes", "08:00-10:00"), ("Lunes", "10:00-12:00")]
    salones = ["S101"]
    r = a_estrella(clases, franjas, salones)
    validar_horario(r, clases)
    asig = r["solucion"]
    assert asig[0][1:3] != asig[1][1:3], "Las clases no deben compartir franja"
    print(f"   -> OK: Clases asignadas en franjas separadas ({asig[0][1:3]} y {asig[1][1:3]}).")


def test_conflicto_grupo():
    print("4. Probando conflicto de grupo (2 clases mismo grupo, 2 franjas, 1 salon)...")
    clases = [
        Clase("C1", "Fisica", "P1", "G_A"),
        Clase("C2", "Quimica", "P2", "G_A"),
    ]
    franjas = [("Lunes", "08:00-10:00"), ("Lunes", "10:00-12:00")]
    salones = ["S101"]
    r = a_estrella(clases, franjas, salones)
    validar_horario(r, clases)
    asig = r["solucion"]
    assert asig[0][1:3] != asig[1][1:3], "El grupo no puede tener dos clases simultaneas"
    print(f"   -> OK: Clases del mismo grupo asignadas en franjas distintas.")


def test_conflicto_salon():
    print("5. Probando conflicto de salon (2 clases, 1 franja, 2 salones)...")
    clases = [
        Clase("C1", "Materia 1", "P1", "G1"),
        Clase("C2", "Materia 2", "P2", "G2"),
    ]
    franjas = [("Lunes", "08:00-10:00")]
    salones = ["S101", "S102"]
    r = a_estrella(clases, franjas, salones)
    validar_horario(r, clases)
    asig = r["solucion"]
    assert asig[0][3] != asig[1][3], "No pueden usar el mismo salon en la misma franja"
    print(f"   -> OK: Ambas clases en la misma franja pero en salones distintos ({asig[0][3]} vs {asig[1][3]}).")


def test_prechequeos_imposibilidad():
    print("6. Probando deteccion por prechequeo de casos imposibles...")
    
    c_muchas = [Clase(f"C{i}", f"M{i}", f"P{i}", f"G{i}") for i in range(5)]
    r1 = a_estrella(c_muchas, [("Lunes", "08-10"), ("Lunes", "10-12")], ["S1"])
    assert r1["encontro_solucion"] is False
    assert r1["nodos_explorados"] == 0
    assert "mas clases que pares" in r1["motivo"]
    print(f"   -> 6.1 Exceso de clases detectado: {r1['motivo']} (0 nodos).")

    c_prof = [
        Clase("C1", "M1", "P1", "G1"),
        Clase("C2", "M2", "P1", "G2"),
        Clase("C3", "M3", "P1", "G3"),
    ]
    r2 = a_estrella(c_prof, [("Lunes", "08-10"), ("Lunes", "10-12")], ["S1", "S2", "S3"])
    assert r2["encontro_solucion"] is False
    assert r2["nodos_explorados"] == 0
    assert "profesor P1 tiene mas clases" in r2["motivo"]
    print(f"   -> 6.2 Sobrecarga de profesor detectada: {r2['motivo']} (0 nodos).")

    c_grupo = [
        Clase("C1", "M1", "P1", "G_SOBRE"),
        Clase("C2", "M2", "P2", "G_SOBRE"),
        Clase("C3", "M3", "P3", "G_SOBRE"),
    ]
    r3 = a_estrella(c_grupo, [("Lunes", "08-10"), ("Lunes", "10-12")], ["S1", "S2", "S3"])
    assert r3["encontro_solucion"] is False
    assert r3["nodos_explorados"] == 0
    assert "grupo G_SOBRE tiene mas clases" in r3["motivo"]
    print(f"   -> 6.3 Sobrecarga de grupo detectada: {r3['motivo']} (0 nodos).")


def test_imposible_en_arbol():
    print("7. Probando caso imposible en arbol (con prechequeo desactivado)...")
    clases = [
        Clase("C1", "M1", "P_UNICO", "G1"),
        Clase("C2", "M2", "P_UNICO", "G2"),
    ]
    franjas = [("Lunes", "08:00-10:00")]
    salones = ["S101", "S102"]
    r = a_estrella(clases, franjas, salones, prechequeo=False)
    assert r["encontro_solucion"] is False
    assert r["solucion"] is None
    assert r["nodos_explorados"] > 0
    print(f"   -> OK: Recorrio el arbol y determino que no hay solucion ({r['nodos_explorados']} nodos).")


def test_preferencia_blanda_optimizacion():
    print("8. Probando optimizacion de restriccion blanda (evitar franja bloqueada)...")
    clase = [Clase("C1", "Calculo", "PROF_X", "G1")]
    franjas = [("Lunes", "08:00-10:00"), ("Martes", "10:00-12:00")]
    salones = ["S101"]
    
    no_disp = {"PROF_X": ("Lunes", "08:00-10:00")}
    r = a_estrella(clase, franjas, salones, no_disp)
    validar_horario(r, clase)
    asig = r["solucion"][0]
    
    assert asig[1:3] == ("Martes", "10:00-12:00"), "Debio escoger Martes para no ser penalizado"
    assert r["costo_solucion"] == 1, "El costo debe ser 1 (optimo sin penalizar)"
    print(f"   -> OK: A* eligio la franja disponible {asig[1:3]} con costo optimo {r['costo_solucion']}.")


def test_penalizacion_inevitable():
    print("9. Probando penalizacion inevitable...")
    # Solo hay una franja y coincide con la que el profesor no puede
    clase = [Clase("C1", "Calculo", "PROF_Y", "G1")]
    franjas = [("Lunes", "08:00-10:00")]
    salones = ["S101"]
    no_disp = {"PROF_Y": ("Lunes", "08:00-10:00")}
    
    r = a_estrella(clase, franjas, salones, no_disp)
    validar_horario(r, clase)
    assert r["costo_solucion"] == 6, "1 por clase + 5 por penalizacion = 6"
    print(f"   -> OK: A* encontro solucion valida pagando la penalizacion obligada: costo {r['costo_solucion']}.")


def test_tope_de_nodos():
    print("10. Probando tope de nodos (max_nodos)...")
    # Con max_nodos = 1, para 3 clases debe abortar por limite
    clases = [
        Clase("C1", "M1", "P1", "G1"),
        Clase("C2", "M2", "P2", "G2"),
        Clase("C3", "M3", "P3", "G3"),
    ]
    franjas = [("Lunes", "08-10"), ("Lunes", "10-12"), ("Lunes", "12-14")]
    salones = ["S1"]
    r = a_estrella(clases, franjas, salones, max_nodos=1)
    assert r["limite_alcanzado"] is True
    assert r["encontro_solucion"] is False
    print(f"   -> OK: Se detuvo limpiamente por limite_alcanzado ({r['nodos_explorados']} nodos).")


def test_escalabilidad_datos_reales():
    print("11. Probando escalabilidad sobre el dataset oficial (archivos/)...")
    ruta_archivos = os.path.join(ruta_proyecto, "archivos")
    cursos = cargar_cursos(os.path.join(ruta_archivos, "cursos.txt"))
    franjas = cargar_franjas(os.path.join(ruta_archivos, "franjas.txt"))
    salones = cargar_salones(os.path.join(ruta_archivos, "salones.txt"))
    profesores = cargar_profesores(os.path.join(ruta_archivos, "profesores.txt"))

    for n in [1, 2, 5, 10, 15, 20]:
        sub_cursos = cursos[:n]
        r = a_estrella(sub_cursos, franjas, salones, profesores, max_nodos=50000)
        validar_horario(r, sub_cursos)
        assert r["costo_solucion"] == n, f"Costo esperado {n}, obtenido {r['costo_solucion']}"
        print(f"   -> {n:>2} clases: OK | Nodos: {r['nodos_explorados']:>2} | Costo: {r['costo_solucion']:>2} | Tiempo: {r['tiempo_ejecucion']:.4f} s")


def test_simetria_activada_vs_desactivada():
    print("12. Probando romper_simetria_salones=True vs False...")
    clases = [
        Clase("C1", "M1", "P1", "G1"),
        Clase("C2", "M2", "P2", "G2"),
    ]
    franjas = [("Lunes", "08-10"), ("Lunes", "10-12")]
    salones = [f"S{i}" for i in range(10)]
    
    # Con simetria rota (menos ramas)
    r_sim = a_estrella(clases, franjas, salones, romper_simetria_salones=True)
    validar_horario(r_sim, clases)
    
    # Sin romper simetria (prueba todos los salones)
    r_no_sim = a_estrella(clases, franjas, salones, romper_simetria_salones=False)
    validar_horario(r_no_sim, clases)
    
    print(f"   -> Romper simetria True:  Nodos = {r_sim['nodos_explorados']}")
    print(f"   -> Romper simetria False: Nodos = {r_no_sim['nodos_explorados']}")
    assert r_sim["encontro_solucion"] and r_no_sim["encontro_solucion"]
    print("   -> OK: Ambos modos encontraron horarios validos sin conflictos.")


def main():
    print("=" * 70)
    print(" SUITE DE TESTEO PARA CASOS ESPECIFICOS: ALGORITMO A* ")
    print("=" * 70)
    test_caso_vacio()
    test_caso_minimo()
    test_conflicto_profesor()
    test_conflicto_grupo()
    test_conflicto_salon()
    test_prechequeos_imposibilidad()
    test_imposible_en_arbol()
    test_preferencia_blanda_optimizacion()
    test_penalizacion_inevitable()
    test_tope_de_nodos()
    test_simetria_activada_vs_desactivada()
    test_escalabilidad_datos_reales()
    print("=" * 70)
    print(" TODOS LOS 12 CASOS ESPECIFICOS PASARON EXITOSAMENTE (100% OK) ")
    print("=" * 70)


if __name__ == "__main__":
    main()
