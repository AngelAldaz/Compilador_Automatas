import tkinter as tk
from tkinter import ttk
from compiler import compilar_codigo
from utils import actualizar_lineas
from config import TEXTO_INICIAL
from optimizacion import detectar_optimizaciones, aplicar_optimizacion

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

  # ========== LADO DERECHO (Notebook con pestañas) ==========
  notebook = ttk.Notebook(paned_horizontal)
  paned_horizontal.add(notebook, minsize=400)

  # ========== PESTAÑA 1: Compilación (Lexemas + Errores) ==========
  tab_compilacion = tk.Frame(notebook, bg="#f0f0f0")
  notebook.add(tab_compilacion, text="Compilación")

  # PanedWindow vertical para dividir lexemas y errores
  paned_derecho = tk.PanedWindow(tab_compilacion, orient=tk.VERTICAL, sashrelief=tk.RAISED)
  paned_derecho.pack(fill="both", expand=True)

  # Frame para botón y tabla de lexemas
  frame_lexemas = tk.Frame(paned_derecho, bg="#f0f0f0")
  paned_derecho.add(frame_lexemas, stretch="always")

  # Botón de compilar
  btn_compilar = tk.Button(
      frame_lexemas, text="Compilar", 
      command=lambda: [
          compilar_codigo(editor, tabla, tabla_dicc, tabla_triplos),
          actualizar_tabla_optimizacion(editor, tabla_opt_original, tabla_opt_optimizada)
      ],
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

  # Frame para tabla de errores
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

  # ========== PESTAÑA 2: Optimización ==========
  tab_optimizacion = tk.Frame(notebook, bg="#f0f0f0")
  notebook.add(tab_optimizacion, text="Optimización")

  # Frame para información de optimización
  frame_opt_info = tk.Frame(tab_optimizacion, bg="#f0f0f0")
  frame_opt_info.pack(fill="x", padx=10, pady=10)

  label_opt_titulo = tk.Label(
      frame_opt_info, 
      text="Técnica de Optimización: Eliminación de Código Redundante",
      bg="#f0f0f0", 
      font=("Segoe UI", 11, "bold"),
      fg="#d35400"
  )
  label_opt_titulo.pack(anchor="w")

  label_opt_desc = tk.Label(
      frame_opt_info,
      text="Instrucciones que se repiten sin haber tenido modificación alguna en uno de sus valores",
      bg="#f0f0f0",
      font=("Segoe UI", 9),
      fg="#555555"
  )
  label_opt_desc.pack(anchor="w", pady=(2, 0))

  # PanedWindow horizontal para dividir las dos tablas
  paned_opt = tk.PanedWindow(tab_optimizacion, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
  paned_opt.pack(fill="both", expand=True, padx=10, pady=5)

  # Frame para código original
  frame_opt_original = tk.Frame(paned_opt, bg="#f0f0f0")
  paned_opt.add(frame_opt_original, stretch="always")

  label_opt_original = tk.Label(
      frame_opt_original,
      text="Código de Entrada (Original)",
      bg="#f0f0f0",
      font=("Segoe UI", 10, "bold")
  )
  label_opt_original.pack(pady=5, padx=5, anchor="w")

  # Tabla para código original con líneas resaltadas
  tabla_opt_original = ttk.Treeview(
      frame_opt_original,
      columns=("Línea", "Código"),
      show="headings",
      height=20
  )
  tabla_opt_original.heading("Línea", text="Línea")
  tabla_opt_original.heading("Código", text="Código")
  tabla_opt_original.column("Línea", width=50, anchor="center")
  tabla_opt_original.column("Código", width=300, anchor="w")
  tabla_opt_original.pack(fill="both", expand=True, padx=5, pady=5)

  # Frame para código optimizado
  frame_opt_optimizada = tk.Frame(paned_opt, bg="#f0f0f0")
  paned_opt.add(frame_opt_optimizada, stretch="always")

  label_opt_optimizada = tk.Label(
      frame_opt_optimizada,
      text="Código Optimizado",
      bg="#f0f0f0",
      font=("Segoe UI", 10, "bold")
  )
  label_opt_optimizada.pack(pady=5, padx=5, anchor="w")

  # Tabla para código optimizado
  tabla_opt_optimizada = ttk.Treeview(
      frame_opt_optimizada,
      columns=("Línea", "Código"),
      show="headings",
      height=20
  )
  tabla_opt_optimizada.heading("Línea", text="Línea")
  tabla_opt_optimizada.heading("Código", text="Código")
  tabla_opt_optimizada.column("Línea", width=50, anchor="center")
  tabla_opt_optimizada.column("Código", width=300, anchor="w")
  tabla_opt_optimizada.pack(fill="both", expand=True, padx=5, pady=5)

  # Estilo de la tabla: colores estándar (no cambia)
  style = ttk.Style()
  style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white", font=("Consolas", 10))
  style.map('Treeview', background=[('selected', '#007acc')], foreground=[('selected', 'white')])
  
  # Estilo especial para líneas optimizadas (amarillo)
  tabla_opt_original.tag_configure('optimizada', background='#fff3cd', foreground='#856404')

  # Función para actualizar la tabla de optimización
  def actualizar_tabla_optimizacion(editor, tabla_original, tabla_optimizada):
      codigo = editor.get("1.0", "end").strip()
      lineas = codigo.split('\n')
      
      # Detectar líneas optimizables
      lineas_optimizables = detectar_optimizaciones(codigo)
      
      # Aplicar optimización (obtiene código con sustituciones y líneas modificadas)
      codigo_optimizado, _, lineas_modificadas = aplicar_optimizacion(codigo)
      lineas_optimizadas = codigo_optimizado.split('\n')
      
      # Limpiar tablas
      for item in tabla_original.get_children():
          tabla_original.delete(item)
      for item in tabla_optimizada.get_children():
          tabla_optimizada.delete(item)
      
      # Llenar tabla original (con resaltado amarillo en líneas optimizables Y modificadas)
      for i, linea in enumerate(lineas):
          num_linea = i + 1
          if num_linea in lineas_optimizables or num_linea in lineas_modificadas:
              # Línea optimizable o modificada - resaltar en amarillo
              tabla_original.insert("", "end", values=(num_linea, linea), tags=('optimizada',))
          else:
              # Línea normal
              tabla_original.insert("", "end", values=(num_linea, linea))
      
      # Llenar tabla optimizada (con el código que incluye sustituciones)
      for i, linea in enumerate(lineas_optimizadas):
          num_linea_opt = i + 1
          tabla_optimizada.insert("", "end", values=(num_linea_opt, linea))

  return root
