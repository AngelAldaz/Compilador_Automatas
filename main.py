import re
import tkinter as tk
from tkinter import ttk, scrolledtext

# Expresión regular para los identificadores
id_regex = r"id_[A-Za-z0-9_-]+"
regex_string = r'"([^"]+)"'


# Tipos de datos
# tipos = ["num", "chain", "cow"]
tipos = {"num": "int", "chain": "str", "cow": "float"}

def tipar_lista(valores):
  def convertir(valor: str):
    try:
      return int(valor)
    except ValueError:
      try:
        return float(valor)
      except ValueError:
        return valor
  return [convertir(v) for v in valores]

def compilar_codigo():
  codigo = editor.get("1.0", tk.END).strip()  # quitar espacios innecesarios
  lexemaDict = {}

  for linea in codigo.split("\n"):
    lexemas = linea.split()
    # Obtener el tipo de línea basado en los lexemas presentes
    tipo_de_linea = next((t for t in tipos if t in lexemas), None)
    lexemas = tipar_lista(lexemas)
    # print(lexemas)
    token_error_dup = 1
    for lexema in lexemas:
      if lexema not in lexemaDict:
        if re.match(id_regex, str(lexema)):
          lexemaDict[str(lexema)] = tipo_de_linea or "Indeterminado"
        else:
          try:
            for tipo, tipo_nombre in tipos.items():
              # print(tipo, tipo_nombre, type(lexema).__name__)
              if re.match(regex_string, str(lexema)):
                lexemaDict[str(lexema)] = "chain"
                break
              if tipo_nombre == type(lexema).__name__:
                if tipo == "chain":
                  lexemaDict[str(lexema)] = ""
                  break
                else:
                  lexemaDict[str(lexema)] = tipo
                  break
          except:
            # if type(lexema) in tipos.values():
            #   lexemaDict[str(lexema)] = "literal"
            lexemaDict[str(lexema)] = ""
  # print(lexemaDict)
  # Limpiar la tabla
  for item in tabla.get_children():
    tabla.delete(item)
    

  # Insertar en la tabla desde el diccionario
  for lex, tipo in lexemaDict.items():
    if tipo == "Indeterminado":
      tabla.insert("", tk.END, values=(lex, ""))
    else:
      tabla.insert("", tk.END, values=(lex, tipo))
    autoajustar_columnas(tabla)
  compilar_errores(lexemaDict)
    
    
def compilar_errores(lexemaDict):
  codigo = editor.get("1.0", tk.END).strip()  # quitar espacios innecesarios
  lineas = codigo.split("\n")
  lineas_recorridas = 0
  
  token_error_asignacion = 1
  token_error_operacion = 1
  token_error_tipo = 1
  token_error_declaracion = 1  
  
  identificadores_declarados = set() 
   
  for linea in lineas:
    linea_de_lexemas = linea.split()
    linea_de_tipos = []
    
    # --- Detectar declaración ---
    if linea_de_lexemas and linea_de_lexemas[0] in ["num", "cow"]:  
      # después del tipo vienen los identificadores, separados por coma
      ids = [x.strip().strip(",") for x in linea_de_lexemas[1:] if x != ","]

      for identificador in ids:
        if identificador in identificadores_declarados:
          # Declaración duplicada
          token = f"ED{token_error_declaracion}"
          token_error_declaracion += 1
          descripcion = f"Error de declaración duplicada: El lexema ya fue declarado"
          linea_error = lineas_recorridas + 1
          tabla_dicc.insert("", tk.END, values=(token, linea_error, identificador, descripcion))
          autoajustar_columnas(tabla_dicc)
        else:
          identificadores_declarados.add(identificador)
    
    if "=" in linea_de_lexemas:
      for lexema in linea_de_lexemas:
        linea_de_tipos.append(lexemaDict.get(lexema))
      if "Indeterminado" in linea_de_tipos:
        indices = [i for i, x in enumerate(linea_de_tipos) if x == "Indeterminado"] 
        for indice in indices:
          linea_error = lineas_recorridas+1
          lexema_error = linea_de_lexemas[indice]
          if not any(op in linea_de_lexemas for op in ["+","-","*","/"]):
            token = f"EA{token_error_asignacion}"
            token_error_asignacion += 1
            descripcion = "Error de asignación: Lexema indeterminado"
            tabla_dicc.insert("", tk.END, values=(token, linea_error, lexema_error, descripcion))
            autoajustar_columnas(tabla_dicc)
            # print(f"Error de asignación: Lexema {lexema_error} indeterminado en línea número {linea_error}")
          else:
            token = f"EO{token_error_operacion}"
            token_error_operacion += 1
            descripcion = "Error de operacion: Lexema indeterminado"
            tabla_dicc.insert("", tk.END, values=(token, linea_error, lexema_error, descripcion))
            autoajustar_columnas(tabla_dicc)
            # print(f"Error de operacion: Lexema {lexema_error} indeterminado en línea número {linea_error}")
      else:
        # if not any(op in linea_de_lexemas for op in ["+","-","*","/"]):
        #   # Duplicacion de asignación
          
        if not any(all(x in ('', tipo) for x in linea_de_tipos) for tipo in tipos):
          linea_error = lineas_recorridas + 1
          # Determinar tipo esperado (el más común en la línea, ignorando vacíos)
          tipos_validos = [t for t in linea_de_tipos if t not in ('', None)]
          if tipos_validos:
            tipo_esperado = max(set(tipos_validos), key=tipos_validos.count)
          else:
            tipo_esperado = None

          # Buscar el primer lexema que no coincida con el tipo esperado
          lexema_error = None
          for lexema, tipo_detectado in zip(linea_de_lexemas, linea_de_tipos):
            if tipo_detectado not in ('', None) and tipo_detectado != tipo_esperado:
              lexema_error = lexema
              break
          token = f"ET{token_error_tipo}"
          token_error_tipo += 1
          descripcion = f"Error de tipo: Incompatiblidad de tipos, {tipo_esperado}"
          tabla_dicc.insert("", tk.END, values=(token, linea_error, lexema_error, descripcion))
          autoajustar_columnas(tabla_dicc)
          # print(linea)
          # print(linea_de_tipos)
          # print(f"Error de tipo: Operación inválida en línea número {linea_error} por lexema {lexema_error}")
    lineas_recorridas += 1


# Función para actualizar los números de línea
def actualizar_lineas(event=None):
  lineas = "\n".join(str(i+1) for i in range(int(editor.index('end-1c').split('.')[0])))
  lineas_text.config(state='normal')
  lineas_text.delete('1.0', 'end')
  lineas_text.insert('1.0', lineas)
  lineas_text.config(state='disabled')

# Función para ajustar el ancho de las columnas
def autoajustar_columnas(treeview):
  for col in treeview["columns"]:
    # iniciar con el ancho del encabezado
    max_len = len(col)
    # recorrer todos los ítems de la columna
    for item in treeview.get_children():
      valor = treeview.set(item, col)
      if valor:
        max_len = max(max_len, len(str(valor)))
    # ajustar ancho: multiplicar por un factor (px aproximados por carácter)
    treeview.column(col, width=(max_len * 8))


# Crear ventana principal con tamaño fijo
root = tk.Tk()
root.title("Editor de Código")
root.geometry("1300x600")
# root.resizable(False, False)
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
editor.bind('<KeyRelease>', actualizar_lineas)

# Texto inicial en el editor
texto_inicial ="""num id_int1 , id_int2 , id_int3
cow id_real1 , id_real2 , id_real3
chain id_cadena1 , id_cadena2 , id_cadena3
id_int1 = id_int2 + id_cadena1
id_cadena1 = id_cadena2 + id_int2
id_cadena3 = id_cadena2 + id_real2
id_int1 = id_cadena1
id_int2 = id_cadena2
id_int3 = id_cadena3
id_int1 = id_int2 + id_int4
id_cadena1 = id_cadena2 + id_cadena4
id_real1 = id_real2 + id_real4
id_int3 = id_int5
id_cadena3 = id_cadena5
id_real3 = id_real5
num id_int1
cow id_real1
for id_int1 5 {
id_int2 = id_int3 + 1
}
"""
editor.insert('1.0', texto_inicial)
actualizar_lineas()

# Frame para la tabla y botón (lado derecho)
frame_tabla = tk.Frame(paned, bg="#f0f0f0", width=300)
paned.add(frame_tabla, minsize=250)

# Botón de compilar en el frame derecho
btn_compilar = tk.Button(
    frame_tabla, text="Compilar", command=compilar_codigo,
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

# Nueva tabla: Diccionario de símbolos
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

root.mainloop()
