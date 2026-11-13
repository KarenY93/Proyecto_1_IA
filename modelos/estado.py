from typing import FrozenSet, Optional, Tuple

try:
    from .clase import Clase
except ImportError:
    from modelos.clase import Clase

# Formato de una asignacion: (id_clase, dia, franja, salon)
Asignacion = Tuple[str, str, str, str]
# Formato de un recurso ocupado: (dia, franja, tipo_recurso, id_recurso)
Ocupacion = Tuple[str, str, str, str]


class Estado:
    """Guarda las asignaciones hechas y los recursos ocupados para verificar restricciones.

    Es inmutable en la practica: asignar() devuelve un estado nuevo.
    La clave de igualdad (frozenset de asignaciones) se calcula solo si se
    necesita comparar o hacer hash, para no pagar ese costo en cada nodo.
    """

    __slots__ = ("asignaciones", "_ids", "_ocupados", "_clave", "_hash")

    def __init__(
        self,
        asignaciones: Tuple[Asignacion, ...] = (),
        ocupados: FrozenSet[Ocupacion] = frozenset(),
        ids: Optional[FrozenSet[str]] = None,
    ) -> None:
        self.asignaciones = asignaciones
        # Al crear un hijo se pasa 'ids' ya calculado: evita recorrer todo.
        self._ids = ids if ids is not None else frozenset(a[0] for a in asignaciones)
        self._ocupados = ocupados
        self._clave: Optional[FrozenSet[Asignacion]] = None
        self._hash: Optional[int] = None

    @staticmethod
    def _recursos(clase: Clase, dia: str, franja: str, salon: str):
        # Recursos que quedan ocupados en esa franja
        return (
            (dia, franja, "salon", salon),
            (dia, franja, "profesor", clase.id_profesor),
            (dia, franja, "grupo", clase.grupo),
        )

    def esta_asignada(self, id_clase: str) -> bool:
        return id_clase in self._ids

    def puede_en_franja(self, clase: Clase, dia: str, franja: str) -> bool:
        """Profesor y grupo libres en la franja (no depende del salon)."""
        return (
            (dia, franja, "profesor", clase.id_profesor) not in self._ocupados
            and (dia, franja, "grupo", clase.grupo) not in self._ocupados
        )

    def salon_libre(self, dia: str, franja: str, salon: str) -> bool:
        return (dia, franja, "salon", salon) not in self._ocupados

    def puede_asignar(self, clase: Clase, dia: str, franja: str, salon: str) -> bool:
        """Verifica que no haya choques de salon, profesor o grupo en la misma franja."""
        if clase.id_curso in self._ids:
            return False
        return self.puede_en_franja(clase, dia, franja) and self.salon_libre(
            dia, franja, salon
        )

    def asignar(
        self, clase: Clase, dia: str, franja: str, salon: str, verificar: bool = True
    ) -> "Estado":
        """Devuelve un nuevo estado con la asignacion agregada.

        verificar=False se usa cuando quien llama ya comprobo las restricciones
        (generar_sucesores), para no validar dos veces.
        """
        if verificar and not self.puede_asignar(clase, dia, franja, salon):
            raise ValueError(
                f"No se puede asignar {clase.id_curso!r} en {dia} {franja} ({salon})."
            )
        return Estado(
            self.asignaciones + ((clase.id_curso, dia, franja, salon),),
            self._ocupados | frozenset(self._recursos(clase, dia, franja, salon)),
            self._ids | {clase.id_curso},
        )

    def _obtener_clave(self) -> FrozenSet[Asignacion]:
        if self._clave is None:
            self._clave = frozenset(self.asignaciones)
        return self._clave

    def __len__(self) -> int:
        return len(self.asignaciones)

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Estado):
            return NotImplemented
        return self._obtener_clave() == otro._obtener_clave()

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(self._obtener_clave())
        return self._hash

    def __repr__(self) -> str:
        return f"Estado({len(self)} asignadas)"