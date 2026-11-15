class Nodo:
    """Nodo que representa un paso en el arbol de busqueda."""

    def __init__(self, estado, padre=None, accion=None, g=0, h=0):
        self.estado = estado          # Estado actual del horario
        self.padre = padre            # Nodo anterior
        self.accion = accion          # Asignacion hecha: (id_curso, dia, franja, salon)
        self.g = g                    # Costo real acumulado
        self.h = h                    # Estimacion heuristica hasta la meta
        self.f = g + h                # Evaluacion f(n) = g(n) + h(n)

    def __lt__(self, otro):
        # Desempate: si f es igual, preferimos el que tenga menor h (mas cerca de la meta)
        if self.f == otro.f:
            return self.h < otro.h
        return self.f < otro.f

