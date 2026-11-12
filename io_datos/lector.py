import os

try:
    from modelos.clase import Clase
except ImportError:
    from ..modelos.clase import Clase


def cargar_cursos(ruta_archivo):
    """Lee el archivo cursos.txt y devuelve una lista de objetos Clase."""
    cursos = []
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = [p.strip() for p in linea.split(",")]
            if len(partes) >= 4:
                cursos.append(Clase(
                    id_curso=partes[0],
                    nombre_materia=partes[1],
                    id_profesor=partes[2],
                    grupo=partes[3]
                ))
    return cursos


def cargar_franjas(ruta_archivo):
    """Lee franjas.txt y devuelve una lista de tuplas (dia, franja_horaria)."""
    franjas = []
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = [p.strip() for p in linea.split(",")]
            if len(partes) >= 3:
                dia = partes[0]
                franja = f"{partes[1]}-{partes[2]}"
                franjas.append((dia, franja))
    return franjas


def cargar_salones(ruta_archivo):
    """Lee salones.txt y devuelve una lista de nombres de salones."""
    salones = []
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = [p.strip() for p in linea.split(",")]
            if partes:
                salones.append(partes[0])
    return salones


def cargar_profesores(ruta_archivo):
    """Lee profesores.txt y devuelve un diccionario con los horarios no disponibles."""
    profesores = {}
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = [p.strip() for p in linea.split(",")]
            if len(partes) >= 6:
                id_prof = partes[0]
                dia_no = partes[3].replace("(", "").strip()
                h_ini = partes[4].strip()
                h_fin = partes[5].replace(")", "").strip()
                profesores[id_prof] = (dia_no, f"{h_ini}-{h_fin}")
    return profesores
