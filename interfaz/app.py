"""Interfaz grafica (Tkinter) del sistema de asignacion de horarios.

Paneles:
  1. Carga de archivos (boton Examinar, ruta y estado de lectura).
  2. Configuracion (algoritmo) y boton "Generar Horario".
  3. Grilla del horario (filas = franjas, columnas = dias).
  4. Estadisticas comparativas de los algoritmos ya ejecutados.

El algoritmo se ejecuta en un hilo aparte para que la ventana no se congele
(BFS y costo uniforme pueden tardar). El hilo devuelve el resultado por una
cola y la ventana la revisa periodicamente con after().
"""
import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Permite ejecutar este archivo directamente desde cualquier carpeta.
RUTA_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RUTA_PROYECTO not in sys.path:
    sys.path.insert(0, RUTA_PROYECTO)

from algoritmos.a_estrella import a_estrella
from algoritmos.bfs import bfs
from algoritmos.costo_uniforme import costo_uniforme
from algoritmos.profundidad_iterativa import profundidad_iterativa
from io_datos.lector import (
    cargar_cursos,
    cargar_franjas,
    cargar_nombres_profesores,
    cargar_profesores,
    cargar_salones,
)

# Tope de nodos para los algoritmos que lo aceptan (protege memoria y tiempo).
MAX_NODOS = 50000

# nombre en el menu -> (nombre corto, funcion, acepta max_nodos)
ALGORITMOS = {
    "Amplitud (BFS)": ("BFS", bfs, True),
    "Costo uniforme": ("Costo uniforme", costo_uniforme, True),
    "Profundidad iterativa": ("Prof. iterativa", profundidad_iterativa, True),
    "A* (informado)": ("A*", a_estrella, True),
}

# clave, nombre del archivo, funcion lectora
ARCHIVOS = [
    ("profesores", "profesores.txt", cargar_profesores),
    ("cursos", "cursos.txt", cargar_cursos),
    ("salones", "salones.txt", cargar_salones),
    ("franjas", "franjas.txt", cargar_franjas),
]

COLOR_OK = "#1b7f3b"
COLOR_ERROR = "#b00020"
COLOR_LIBRE = "#e6e6e6"
COLOR_OCUPADA = "#dbeafe"


class App(tk.Tk):
    """Ventana principal de la aplicacion."""

    def __init__(self):
        super().__init__()
        self.title("Programacion Academica Universitaria")
        self.geometry("1100x720")
        self.minsize(900, 600)

        self.datos = {}              # clave -> datos leidos del archivo
        self.var_ruta = {}           # clave -> StringVar con la ruta
        self.var_estado = {}         # clave -> StringVar con el indicador
        self.lbl_estado = {}         # clave -> Label (para cambiar el color)
        self.nombres_prof = {}       # id_profesor -> "Nombre Apellido"
        self.solucion = None         # ultima solucion mostrada
        self.cola = queue.Queue()    # resultados que envia el hilo

        self._crear_panel_archivos()
        self._crear_panel_configuracion()
        self._crear_panel_estadisticas()   # va antes: se ancla abajo
        self._crear_panel_horario()

    # ------------------------------------------------------------------
    # Construccion de paneles
    # ------------------------------------------------------------------
    def _crear_panel_archivos(self):
        marco = ttk.LabelFrame(self, text="Archivos de entrada")
        marco.pack(fill="x", padx=10, pady=(10, 5))
        marco.columnconfigure(1, weight=1)

        for fila, (clave, nombre, _) in enumerate(ARCHIVOS):
            self.var_ruta[clave] = tk.StringVar(value="(sin cargar)")
            self.var_estado[clave] = tk.StringVar(value="Pendiente")

            ttk.Button(
                marco, text=f"Cargar {nombre}", width=24,
                command=lambda c=clave: self._examinar(c),
            ).grid(row=fila, column=0, padx=5, pady=2, sticky="w")
            ttk.Label(marco, text="ruta:").grid(row=fila, column=1, sticky="w")
            ttk.Label(marco, textvariable=self.var_ruta[clave]).grid(
                row=fila, column=2, padx=5, sticky="w"
            )
            lbl = tk.Label(marco, textvariable=self.var_estado[clave], fg="gray", width=26, anchor="w")
            lbl.grid(row=fila, column=3, padx=5, sticky="w")
            self.lbl_estado[clave] = lbl

    def _crear_panel_configuracion(self):
        marco = ttk.LabelFrame(self, text="Configuracion")
        marco.pack(fill="x", padx=10, pady=5)

        ttk.Label(marco, text="Algoritmo:").pack(side="left", padx=5, pady=5)
        self.combo_algoritmo = ttk.Combobox(
            marco, values=list(ALGORITMOS), state="readonly", width=26
        )
        self.combo_algoritmo.current(len(ALGORITMOS) - 1)
        self.combo_algoritmo.pack(side="left", padx=5)

        ttk.Label(marco, text="Clases a programar (primeras N):").pack(
            side="left", padx=(15, 5)
        )
        self.var_n = tk.StringVar(value="1")
        self.spin_n = ttk.Spinbox(
            marco, from_=1, to=1, width=5, textvariable=self.var_n
        )
        self.spin_n.pack(side="left")

        self.btn_generar = ttk.Button(
            marco, text="Generar Horario", command=self._generar
        )
        self.btn_generar.pack(side="left", padx=10)

        self.var_mensaje = tk.StringVar(value="")
        ttk.Label(marco, textvariable=self.var_mensaje).pack(side="left", padx=10)

    def _crear_panel_horario(self):
        marco = ttk.LabelFrame(self, text="Horario generado")
        marco.pack(fill="both", expand=True, padx=10, pady=5)

        barra = ttk.Frame(marco)
        barra.pack(fill="x")
        ttk.Label(barra, text="Ver grupo:").pack(side="left", padx=5, pady=3)
        self.combo_grupo = ttk.Combobox(barra, values=["Todos"], state="readonly", width=12)
        self.combo_grupo.current(0)
        self.combo_grupo.pack(side="left")
        self.combo_grupo.bind("<<ComboboxSelected>>", lambda _e: self._dibujar_horario())

        # La grilla vive dentro de un Canvas con barras de desplazamiento,
        # para poder ver el horario completo aunque no quepa en la ventana.
        contenedor = ttk.Frame(marco)
        contenedor.pack(fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(contenedor, highlightthickness=0)
        barra_v = ttk.Scrollbar(contenedor, orient="vertical", command=self.canvas.yview)
        barra_h = ttk.Scrollbar(contenedor, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=barra_v.set, xscrollcommand=barra_h.set)
        barra_v.pack(side="right", fill="y")
        barra_h.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.frame_grilla = ttk.Frame(self.canvas)
        self.id_ventana = self.canvas.create_window(
            (0, 0), window=self.frame_grilla, anchor="nw"
        )
        # Actualiza el area desplazable cuando cambia el tamano de la grilla.
        self.frame_grilla.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        # La grilla ocupa al menos 900 px de ancho (si no cabe, aparece la barra horizontal).
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self.id_ventana, width=max(e.width, 900)),
        )
        # Rueda del mouse: activa solo cuando el cursor esta sobre el horario.
        self.canvas.bind("<Enter>", lambda _e: self._activar_rueda(True))
        self.canvas.bind("<Leave>", lambda _e: self._activar_rueda(False))

    def _activar_rueda(self, activar):
        """Conecta o desconecta la rueda del mouse con el desplazamiento vertical."""
        eventos = ("<MouseWheel>", "<Button-4>", "<Button-5>")
        for evento in eventos:
            if activar:
                self.bind_all(evento, self._rueda)
            else:
                self.unbind_all(evento)

    def _rueda(self, evento):
        """Desplaza el horario (Windows/macOS usan delta; Linux usa Button-4/5)."""
        if evento.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif evento.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-evento.delta / 120) or (-1 if evento.delta > 0 else 1), "units")

    def _crear_panel_estadisticas(self):
        marco = ttk.LabelFrame(self, text="Estadisticas")
        marco.pack(side="bottom", fill="x", padx=10, pady=(5, 10))

        columnas = ("algoritmo", "clases", "nodos", "tiempo", "solucion", "costo")
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=4)
        encabezados = {
            "algoritmo": "Algoritmo", "clases": "Clases", "nodos": "Nodos", "tiempo": "Tiempo",
            "solucion": "Solucion", "costo": "Costo",
        }
        for col in columnas:
            self.tabla.heading(col, text=encabezados[col])
            self.tabla.column(col, anchor="center", width=120)
        self.tabla.pack(fill="x", padx=5, pady=5)

    # ------------------------------------------------------------------
    # Carga de archivos
    # ------------------------------------------------------------------
    def _examinar(self, clave):
        """Abre el selector de archivo y lee el .txt con su funcion lectora."""
        carpeta = os.path.join(RUTA_PROYECTO, "archivos")
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo",
            initialdir=carpeta if os.path.isdir(carpeta) else RUTA_PROYECTO,
            filetypes=[("Archivos de texto", "*.txt")],
        )
        if not ruta:
            return

        lector = next(f for c, _, f in ARCHIVOS if c == clave)
        self.var_ruta[clave].set(ruta)
        try:
            datos = lector(ruta)
            if not datos:
                raise ValueError("vacio o con formato invalido")
        except Exception as error:
            self.datos.pop(clave, None)
            self.var_estado[clave].set(f"Error: {error}")
            self.lbl_estado[clave].config(fg=COLOR_ERROR)
            return

        self.datos[clave] = datos
        if clave == "profesores":
            try:
                self.nombres_prof = cargar_nombres_profesores(ruta)
            except Exception:
                self.nombres_prof = {}
        self.var_estado[clave].set(f"Leido correctamente ({len(datos)})")
        self.lbl_estado[clave].config(fg=COLOR_OK)

        if clave == "cursos":
            grupos = sorted({c.grupo for c in datos})
            self.combo_grupo.config(values=["Todos"] + grupos)
            self.combo_grupo.current(0)
            self.spin_n.config(to=len(datos))
            self.var_n.set(str(len(datos)))

    # ------------------------------------------------------------------
    # Ejecucion del algoritmo
    # ------------------------------------------------------------------
    def _generar(self):
        """Valida que esten los 4 archivos y lanza el algoritmo en un hilo."""
        faltan = [n for c, n, _ in ARCHIVOS if c not in self.datos]
        if faltan:
            messagebox.showwarning(
                "Faltan archivos", "Carga correctamente: " + ", ".join(faltan)
            )
            return

        total = len(self.datos["cursos"])
        try:
            n = int(self.var_n.get())
        except ValueError:
            n = 0
        if not 1 <= n <= total:
            messagebox.showwarning(
                "Numero de clases", f"N debe ser un entero entre 1 y {total}."
            )
            return

        nombre = self.combo_algoritmo.get()
        self.btn_generar.state(["disabled"])
        self.var_mensaje.set(f"Ejecutando {nombre} con {n} clases...")
        threading.Thread(
            target=self._ejecutar, args=(nombre, n), daemon=True
        ).start()
        self.after(100, self._revisar_cola)

    def _ejecutar(self, nombre, n):
        """Corre el algoritmo elegido (en el hilo) y deja el resultado en la cola."""
        _, funcion, con_tope = ALGORITMOS[nombre]
        kwargs = {"max_nodos": MAX_NODOS} if con_tope else {}
        try:
            resultado = funcion(
                self.datos["cursos"][:n], self.datos["franjas"],
                self.datos["salones"], self.datos["profesores"], **kwargs
            )
            resultado["n_clases"] = n
            self.cola.put(("ok", nombre, resultado))
        except Exception as error:
            self.cola.put(("error", nombre, str(error)))

    def _revisar_cola(self):
        """Revisa si el hilo ya termino; si no, vuelve a mirar en 100 ms."""
        try:
            tipo, nombre, contenido = self.cola.get_nowait()
        except queue.Empty:
            self.after(100, self._revisar_cola)
            return

        self.btn_generar.state(["!disabled"])
        if tipo == "error":
            self.var_mensaje.set("")
            messagebox.showerror("Error al ejecutar", contenido)
            return
        self._mostrar_resultado(nombre, contenido)

    def _mostrar_resultado(self, nombre, resultado):
        """Actualiza mensaje, estadisticas y horario con el resultado."""
        corto = ALGORITMOS[nombre][0]
        encontro = resultado["encontro_solucion"]

        if encontro:
            texto_solucion = "Si"
            self.var_mensaje.set(f"{corto}: horario generado.")
        elif resultado.get("limite_alcanzado"):
            texto_solucion = "No (tope de nodos)"
            self.var_mensaje.set(f"{corto}: se alcanzo el tope de {MAX_NODOS} nodos.")
        else:
            texto_solucion = "No"
            motivo = resultado.get("motivo")
            self.var_mensaje.set(
                f"{corto}: sin solucion" + (f" ({motivo})." if motivo else ".")
            )

        costo = resultado.get("costo_solucion")
        valores = (
            corto,
            resultado.get("n_clases", "-"),
            resultado["nodos_explorados"],
            f"{resultado['tiempo_ejecucion']:.4f} s",
            texto_solucion,
            "-" if costo is None else costo,
        )
        if self.tabla.exists(corto):
            self.tabla.item(corto, values=valores)
        else:
            self.tabla.insert("", "end", iid=corto, values=valores)

        if encontro:
            self.solucion = resultado["solucion"]
            self._dibujar_horario()

    # ------------------------------------------------------------------
    # Grilla del horario
    # ------------------------------------------------------------------
    def _dibujar_horario(self):
        """Dibuja la grilla: filas = franjas, columnas = dias."""
        for widget in self.frame_grilla.winfo_children():
            widget.destroy()
        if not self.solucion:
            return

        franjas = self.datos["franjas"]
        dias = list(dict.fromkeys(d for d, _ in franjas))
        horas = list(dict.fromkeys(h for _, h in franjas))
        cursos = {c.id_curso: c for c in self.datos["cursos"]}
        grupo_elegido = self.combo_grupo.get()

        # (dia, hora) -> lista de textos (puede haber varias clases por franja
        # si pertenecen a grupos distintos).
        celdas = {}
        for id_curso, dia, hora, salon in self.solucion:
            curso = cursos[id_curso]
            if grupo_elegido != "Todos" and curso.grupo != grupo_elegido:
                continue
            profesor = self.nombres_prof.get(curso.id_profesor, curso.id_profesor)
            texto = f"{curso.nombre_materia}\nProf. {profesor}\n{salon}"
            if grupo_elegido == "Todos":
                texto += f"\nGrupo {curso.grupo}"
            celdas.setdefault((dia, hora), []).append(texto)

        # Encabezados
        tk.Label(self.frame_grilla, text="Franja", font=("Arial", 9, "bold"),
                 relief="solid", bd=1).grid(row=0, column=0, sticky="nsew")
        for col, dia in enumerate(dias, start=1):
            tk.Label(self.frame_grilla, text=dia, font=("Arial", 9, "bold"),
                     relief="solid", bd=1).grid(row=0, column=col, sticky="nsew")

        # Celdas
        for fila, hora in enumerate(horas, start=1):
            tk.Label(self.frame_grilla, text=hora, font=("Arial", 9, "bold"),
                     relief="solid", bd=1).grid(row=fila, column=0, sticky="nsew")
            for col, dia in enumerate(dias, start=1):
                textos = celdas.get((dia, hora))
                tk.Label(
                    self.frame_grilla,
                    text="\n------\n".join(textos) if textos else "",
                    bg=COLOR_OCUPADA if textos else COLOR_LIBRE,
                    relief="solid", bd=1, justify="left", anchor="nw",
                    wraplength=170, font=("Arial", 8),
                ).grid(row=fila, column=col, sticky="nsew")

        for col in range(len(dias) + 1):
            self.frame_grilla.columnconfigure(col, weight=1)
        for fila in range(1, len(horas) + 1):
            self.frame_grilla.rowconfigure(fila, weight=1)


def main():
    """Punto de entrada: abre la ventana."""
    App().mainloop()


if __name__ == "__main__":
    main()