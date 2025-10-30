import tkinter as tk
from tkinter import ttk
from compiler import compilar_codigo
from utils import actualizar_lineas
from config import TEXTO_INICIAL

def crear_interfaz():
  root = tk.Tk()
  root.title("Editor de Código")
  root.geometry("1400x800")
  root.configure(bg="#2b2b2b")

  # Crear PanedWindow horizontal principal (izquierda-derecha)
  paned_horizontal = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
  paned_horizontal.pack(fill="both", expand=True)

  # ========== LADO IZQUIERDO (Editor + Triplos) ==========
  # PanedWindow vertical para dividir editor y triplos
  paned_izquierdo = tk.PanedWindow(paned_horizontal, orient=tk.VERTICAL, sashrelief=tk.RAISED)
  paned_horizontal.add(paned_izquierdo, stretch="always")

  # Frame del editor (con números de línea) - POSICIÓN (0,0)
  frame_editor = tk.Frame(paned_izquierdo, bg="#2b2b2b")
  paned_izquierdo.add(frame_editor, stretch="always")

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

  # Frame para la tabla de triplos - POSICIÓN (1,0)
  frame_triplos = tk.Frame(paned_izquierdo, bg="#f0f0f0")
  paned_izquierdo.add(frame_triplos, stretch="always")

  # Etiqueta para la tabla de triplos
  label_triplos = tk.Label(frame_triplos, text="Tabla de Triplos", bg="#f0f0f0", font=("Segoe UI", 10, "bold"))
  label_triplos.pack(pady=5, padx=5, anchor="w")

  # Tabla de triplos
  tabla_triplos = ttk.Treeview(frame_triplos, columns=("No. Línea", "Operador", "Dato Objeto", "Dato Fuente"), show="headings")
  tabla_triplos.heading("No. Línea", text="No. Línea")
  tabla_triplos.heading("Operador", text="Operador")
  tabla_triplos.heading("Dato Objeto", text="Dato Objeto")
  tabla_triplos.heading("Dato Fuente", text="Dato Fuente")
  tabla_triplos.pack(fill="both", expand=True, padx=10, pady=5)

  # ========== LADO DERECHO (Lexemas + Errores) ==========
  # PanedWindow vertical para dividir lexemas y errores
  paned_derecho = tk.PanedWindow(paned_horizontal, orient=tk.VERTICAL, sashrelief=tk.RAISED)
  paned_horizontal.add(paned_derecho, minsize=400)

  # Frame para botón y tabla de lexemas - POSICIÓN (0,1)
  frame_lexemas = tk.Frame(paned_derecho, bg="#f0f0f0")
  paned_derecho.add(frame_lexemas, stretch="always")

  # Botón de compilar
  btn_compilar = tk.Button(
      frame_lexemas, text="Compilar", command=lambda: compilar_codigo(editor, tabla, tabla_dicc, tabla_triplos),
      bg="#007acc", fg="white", activebackground="#005f9e",
      relief="flat", font=("Segoe UI", 10, "bold")
  )
  btn_compilar.pack(pady=10, padx=10, fill="x")

  # Etiqueta para tabla de símbolos
  label_lexemas = tk.Label(frame_lexemas, text="Tabla de Símbolos", bg="#f0f0f0", font=("Segoe UI", 10, "bold"))
  label_lexemas.pack(pady=5, padx=10, anchor="w")

  # Tabla de símbolos (lexemas)
  tabla = ttk.Treeview(frame_lexemas, columns=("Lexema", "Tipo"), show="headings")
  tabla.heading("Lexema", text="Lexema")
  tabla.heading("Tipo", text="Tipo")
  tabla.pack(fill="both", expand=True, padx=10, pady=5)

  # Frame para tabla de errores - POSICIÓN (1,1)
  frame_errores = tk.Frame(paned_derecho, bg="#f0f0f0")
  paned_derecho.add(frame_errores, stretch="always")

  # Etiqueta para tabla de errores
  label_errores = tk.Label(frame_errores, text="Tabla de Errores", bg="#f0f0f0", font=("Segoe UI", 10, "bold"))
  label_errores.pack(pady=5, padx=10, anchor="w")

  # Tabla de errores
  tabla_dicc = ttk.Treeview(frame_errores, columns=("Token", "Linea", "Lexema", "Descripción"), show="headings")
  tabla_dicc.heading("Token", text="Token")
  tabla_dicc.heading("Linea", text="Linea")
  tabla_dicc.heading("Lexema", text="Lexema")
  tabla_dicc.heading("Descripción", text="Descripción")
  tabla_dicc.pack(fill="both", expand=True, padx=10, pady=5)

  # Estilo de la tabla: colores estándar (no cambia)
  style = ttk.Style()
  style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white", font=("Consolas", 10))
  style.map('Treeview', background=[('selected', '#007acc')], foreground=[('selected', 'white')])

  return root
