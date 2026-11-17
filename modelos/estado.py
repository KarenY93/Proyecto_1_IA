from modelos.clase import Clase


class Estado:
    def __init__(self, asignaciones=(), ocupados=frozenset(), ids=None):
        self.asignaciones = asignaciones
        # pasamos ids precalculado para no tener que recorrer toda la tupla de asignaciones cada vez
        self._ids = ids if ids is not None else frozenset(a[0] for a in asignaciones)
        # usamos frozenset aca porque buscar choques en listas normales hacia que el CSP fuera lentisimo
        self._ocupados = ocupados

    @staticmethod
    def _recursos(clase, dia, franja, salon):
        return (
            (dia, franja, "salon", salon),
            (dia, franja, "profesor", clase.id_profesor),
            (dia, franja, "grupo", clase.grupo),
        )

    def esta_asignada(self, id_clase):
        return id_clase in self._ids

    def puede_en_franja(self, clase, dia, franja):
        # primero validamos profesor y grupo a nivel de franja; si choca aca, descartamos todos los salones de una
        return (
            (dia, franja, "profesor", clase.id_profesor) not in self._ocupados
            and (dia, franja, "grupo", clase.grupo) not in self._ocupados
        )

    def salon_libre(self, dia, franja, salon):
        return (dia, franja, "salon", salon) not in self._ocupados

    def puede_asignar(self, clase, dia, franja, salon):
        if clase.id_curso in self._ids:
            return False
        return self.puede_en_franja(clase, dia, franja) and self.salon_libre(dia, franja, salon)

    def asignar(self, clase, dia, franja, salon, verificar=True):
        if verificar and not self.puede_asignar(clase, dia, franja, salon):
            # print(f"intento invalido para {clase.id_curso} en {dia} {franja}")
            raise ValueError(f"No se puede asignar {clase.id_curso} en {dia} {franja}")
        
        nuevos_ocupados = self._ocupados | frozenset(self._recursos(clase, dia, franja, salon))
        nuevos_ids = self._ids | {clase.id_curso}
        return Estado(
            self.asignaciones + ((clase.id_curso, dia, franja, salon),),
            nuevos_ocupados,
            nuevos_ids,
        )

    def __len__(self):
        return len(self.asignaciones)

    def __eq__(self, otro):
        if not isinstance(otro, Estado):
            return False
        return set(self.asignaciones) == set(otro.asignaciones)

    def __hash__(self):
        return hash(self.asignaciones)

    def __repr__(self):
        return f"Estado({len(self)} asignadas)"
