import tkinter as tk
from tkinter import ttk
from compiler import compilar_codigo
from utils import actualizar_lineas
from config import TEXTO_INICIAL

def crear_interfaz():
  root = tk.Tk()
  root.title("Editor de Código")
  root.geometry("1300x600")
  root.configure(bg="#2b2b2b")

  # Crear PanedWindow horizontal
  paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
  paned.pack(fill="both", expand=True)

  # Frame del editor (con números de línea)
  frame_editor = tk.Frame(paned, bg="#2b2b2b")
  paned.add(frame_editor, stretch="always")

  # Números de línea
  lineas_text = tk.Text(frame_editor, width=4, bg="#2b2b2b", fg="#888888", font=("Consolas", 12), state='disabled', borderwidth=0, padx=4, highlightthickness=0)
  lineas_text.pack(side="left", fill="y")

  # Editor de código
  editor = tk.Text(frame_editor, font=("Consolas", 12), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
  editor.pack(side="left", fill="both", expand=True)
  editor.bind('<KeyRelease>', lambda e: actualizar_lineas(editor, lineas_text))
  
  # Texto inicial
  editor.insert('1.0', TEXTO_INICIAL)
  actualizar_lineas(editor, lineas_text)

  # Frame para la tabla y botón (lado derecho)
  frame_tabla = tk.Frame(paned, bg="#f0f0f0", width=300)
  paned.add(frame_tabla, minsize=250)

  # Botón de compilar en el frame derecho
  btn_compilar = tk.Button(
      frame_tabla, text="Compilar", command=lambda: compilar_codigo(editor, tabla, tabla_dicc),
      bg="#007acc", fg="white", activebackground="#005f9e",
      relief="flat", font=("Segoe UI", 10, "bold")
  )
  btn_compilar.pack(pady=10, padx=10, fill="x")

  # Contenedor para tablas (vertical)
  frame_contenedor_tablas = tk.Frame(frame_tabla, bg="#f0f0f0")
  frame_contenedor_tablas.pack(fill="both", expand=True, padx=10, pady=5)

  # Tabla de símbolos (lexemas)
  tabla = ttk.Treeview(frame_contenedor_tablas, columns=("Lexema", "Tipo"), show="headings", height=10)
  tabla.heading("Lexema", text="Lexema")
  tabla.heading("Tipo", text="Tipo")
  tabla.pack(fill="both", expand=True, padx=5, pady=5)

  # Tabla de errores
  tabla_dicc = ttk.Treeview(frame_contenedor_tablas, columns=("Token", "Linea", "Lexema", "Descripción"), show="headings", height=10)
  tabla_dicc.heading("Token", text="Token")
  tabla_dicc.heading("Linea", text="Linea")
  tabla_dicc.heading("Lexema", text="Lexema")
  tabla_dicc.heading("Descripción", text="Descripción")
  tabla_dicc.pack(fill="both", expand=True, padx=5, pady=5)

  # Estilo de la tabla: colores estándar (no cambia)
  style = ttk.Style()
  style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white", font=("Consolas", 10))
  style.map('Treeview', background=[('selected', '#007acc')], foreground=[('selected', 'white')])

  return root
