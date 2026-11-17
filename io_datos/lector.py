import os
from modelos.clase import Clase


def cargar_cursos(ruta_archivo):
    cursos = []
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = [p.strip() for p in linea.split(",")]
            if len(partes) >= 4:
                cursos.append(Clase(partes[0], partes[1], partes[2], partes[3]))
    return cursos


def cargar_franjas(ruta_archivo):
    franjas = []
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = [p.strip() for p in linea.split(",")]
            if len(partes) >= 3:
                franjas.append((partes[0], f"{partes[1]}-{partes[2]}"))
    return franjas


def cargar_salones(ruta_archivo):
    salones = []
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = [p.strip() for p in linea.split(",")]
            if partes:
                salones.append(partes[0])
    return salones


def cargar_profesores(ruta_archivo):
    profesores = {}
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for linea in f:
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


def cargar_nombres_profesores(ruta_archivo):
    nombres = {}
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = [p.strip() for p in linea.split(",")]
            if len(partes) >= 3:
                nombres[partes[0]] = f"{partes[1]} {partes[2]}"
    return nombres
