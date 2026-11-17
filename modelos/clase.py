class Clase:
    def __init__(self, id_curso, nombre_materia, id_profesor, grupo, numero_estudiantes=None, tipo_salon=None):
        self.id_curso = id_curso.strip()
        self.nombre_materia = nombre_materia.strip()
        self.id_profesor = id_profesor.strip()
        self.grupo = grupo.strip()
        self.numero_estudiantes = numero_estudiantes
        self.tipo_salon = tipo_salon

    def __repr__(self):
        return f"Clase({self.id_curso}, {self.nombre_materia})"
