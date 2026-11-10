from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Clase:
    """Datos de entrada de una sesión de clase (sin asignación de horario).

    Es inmutable: la búsqueda nunca debe modificarla, solo leerla.
    Cada sesión semanal de una materia es una Clase con id_curso distinto
    (por ejemplo "CAL1-S1", "CAL1-S2").
    """

    id_curso: str
    nombre_materia: str
    id_profesor: str
    grupo: str
    numero_estudiantes: Optional[int] = None
    tipo_salon: Optional[str] = None

    def __post_init__(self) -> None:
        # Detecta errores del .txt al leer, no a mitad de la búsqueda.
        if not self.id_curso.strip():
            raise ValueError("id_curso no puede estar vacío.")
        if self.numero_estudiantes is not None and self.numero_estudiantes < 0:
            raise ValueError(f"numero_estudiantes negativo en {self.id_curso!r}.")