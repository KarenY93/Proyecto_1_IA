from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Clase:
    """Datos de una clase o materia que debe ser programada en el horario."""

    id_curso: str
    nombre_materia: str
    id_profesor: str
    grupo: str
    numero_estudiantes: Optional[int] = None
    tipo_salon: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.id_curso.strip():
            raise ValueError("id_curso no puede estar vacío.")
        if self.numero_estudiantes is not None and self.numero_estudiantes < 0:
            raise ValueError(f"numero_estudiantes negativo en {self.id_curso!r}.")
