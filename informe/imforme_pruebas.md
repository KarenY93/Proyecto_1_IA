# Primera prueba para detectar un adecuado funcionamiento en `clase.py` y `estado.py`

Esta prueba valida que la lógica de asignación de clases funcione correctamente: evita conflictos de profesor, grupo y salón, mantiene la inmutabilidad del estado padre y confirma que el orden de asignación no altera el resultado.

```python
from modelos.clase import Clase
from modelos import estado as modelos

# Clases de prueba: A y B comparten profesor; A y C comparten grupo
a = Clase("A", "Cálculo", "prof1", "g1")
b = Clase("B", "Álgebra", "prof1", "g2")
c = Clase("C", "Física", "prof2", "g1")
d = Clase("D", "Química", "prof3", "g3")

# 1. El padre no cambia al asignar
padre = modelos.Estado()
hijo = padre.asignar(a, "Lunes", "07-09", "S101")
assert len(padre) == 0
assert len(hijo) == 1

# 2. Conflictos de profesor, grupo y salón en el mismo bloque
assert not hijo.puede_asignar(b, "Lunes", "07-09", "S102")  # mismo profesor
assert not hijo.puede_asignar(c, "Lunes", "07-09", "S102")  # mismo grupo
assert not hijo.puede_asignar(d, "Lunes", "07-09", "S101")  # mismo salón
assert hijo.puede_asignar(d, "Lunes", "07-09", "S102")      # sin conflicto
assert hijo.puede_asignar(b, "Lunes", "09-11", "S101")      # otro bloque

# 3. Mismas asignaciones en distinto orden => estados iguales y mismo hash
e1 = modelos.Estado().asignar(a, "Lunes", "07-09", "S101").asignar(d, "Martes", "07-09", "S102")
e2 = modelos.Estado().asignar(d, "Martes", "07-09", "S102").asignar(a, "Lunes", "07-09", "S101")
assert e1 == e2
assert hash(e1) == hash(e2)

# 4. Una clase ya asignada no se puede asignar otra vez
assert not hijo.puede_asignar(a, "Martes", "09-11", "S103")

print("Todas las pruebas pasaron")
```
