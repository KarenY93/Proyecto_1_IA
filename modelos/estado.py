from typing import FrozenSet, Optional, Tuple

from .clase import Clase

# (id_clase, dia, franja, salon)
Asignacion = Tuple[str, str, str, str]
# (dia, franja, tipo_recurso, id_recurso)
Ocupacion = Tuple[str, str, str, str]


class Estado:
    """Asignaciones parciales de una rama de búsqueda.

    Guarda dos cosas:
      - asignaciones: qué clase quedó en qué (día, franja, salón).
      - _ocupados: qué salones, profesores y grupos están ocupados en cada
        (día, franja), para detectar conflictos con una consulta directa.

    No se modifica después de crearse: asignar() devuelve un estado nuevo.
    """

    __slots__ = ("asignaciones", "_ids", "_ocupados", "_clave", "_hash")

    def __init__(
        self,
        asignaciones: Tuple[Asignacion, ...] = (),
        ocupados: FrozenSet[Ocupacion] = frozenset(),
    ) -> None:
        self.asignaciones = asignaciones
        self._ids = frozenset(a[0] for a in asignaciones)
        self._ocupados = ocupados
        # Dos estados con las mismas asignaciones en distinto orden son iguales.
        self._clave = frozenset(asignaciones)
        self._hash: Optional[int] = None

    @staticmethod
    def _recursos(clase: Clase, dia: str, franja: str, salon: str):
        return (
            (dia, franja, "salon", salon),
            (dia, franja, "profesor", clase.id_profesor),
            (dia, franja, "grupo", clase.grupo),
        )

    def esta_asignada(self, id_clase: str) -> bool:
        return id_clase in self._ids

    def puede_asignar(self, clase: Clase, dia: str, franja: str, salon: str) -> bool:
        """True si la clase no está asignada y no choca en salón, profesor ni grupo."""
        if clase.id_curso in self._ids:
            return False
        return not any(
            r in self._ocupados for r in self._recursos(clase, dia, franja, salon)
        )

    def asignar(self, clase: Clase, dia: str, franja: str, salon: str) -> "Estado":
        """Devuelve un estado hijo con la asignación; este estado no cambia."""
        if not self.puede_asignar(clase, dia, franja, salon):
            raise ValueError(
                f"No se puede asignar {clase.id_curso!r} en {dia} {franja} ({salon})."
            )
        return Estado(
            self.asignaciones + ((clase.id_curso, dia, franja, salon),),
            self._ocupados | frozenset(self._recursos(clase, dia, franja, salon)),
        )

    def __len__(self) -> int:
        """Número de clases asignadas (el Problema compara con el total)."""
        return len(self.asignaciones)

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Estado):
            return NotImplemented
        return self._clave == otro._clave

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(self._clave)
        return self._hash

    def __repr__(self) -> str:
        return f"Estado({len(self)} asignadas)"