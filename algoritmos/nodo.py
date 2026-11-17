class Nodo:
    def __init__(self, estado, padre=None, accion=None, g=0, h=0):
        self.estado = estado
        self.padre = padre
        self.accion = accion
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, otro):
        if self.f == otro.f:
            return self.h < otro.h
        return self.f < otro.f
