import re
from config import ID_REGEX, REGEX_STRING, TIPOS
from utils import tipar_lista, autoajustar_columnas
from triplo import generar_triplos

def compilar_codigo(editor, tabla, tabla_dicc, tabla_triplos=None):
  codigo = editor.get("1.0", "end").strip()  # quitar espacios innecesarios
  lexemaDict = {}

  for linea in codigo.split("\n"):
    lexemas = linea.split()
    # Obtener el tipo de línea basado en los lexemas presentes
    tipo_de_linea = next((t for t in TIPOS if t in lexemas), None)
    lexemas = tipar_lista(lexemas)
    
    for lexema in lexemas:
      if lexema not in lexemaDict:
        if re.match(ID_REGEX, str(lexema)):
          lexemaDict[str(lexema)] = tipo_de_linea or "Indeterminado"
        else:
            for tipo, tipo_nombre in TIPOS.items():
              if re.match(REGEX_STRING, str(lexema)):
                lexemaDict[str(lexema)] = "chain"
                break
              if tipo_nombre == type(lexema).__name__:
                lexemaDict[str(lexema)] = "" if tipo == "chain" else tipo
                break
            else:
              lexemaDict[str(lexema)] = ""
              
  # limpiar tabla
  for item in tabla.get_children():
    tabla.delete(item)

  # insertar símbolos
  for lex, tipo in lexemaDict.items():
    tabla.insert("", "end", values=(lex, "" if tipo == "Indeterminado" else tipo))
  autoajustar_columnas(tabla)

  compilar_errores(editor, tabla_dicc, lexemaDict)
  
  # Generar y mostrar triplos si la tabla está disponible
  if tabla_triplos is not None:
    compilar_triplos(editor, tabla_triplos)
  
def compilar_errores(editor, tabla_dicc, lexemaDict):
  codigo = editor.get("1.0", "end").strip()  # quitar espacios innecesarios
  lineas = codigo.split("\n")
  lineas_recorridas = 0
  
  token_error_asignacion = 1
  token_error_operacion = 1
  token_error_tipo = 1
  token_error_declaracion = 1  
  
  identificadores_declarados = set() 
   
  for item in tabla_dicc.get_children():
    tabla_dicc.delete(item)
  for linea in lineas:
    linea_de_lexemas = linea.split()
    linea_de_tipos = []
     # limpiar tabla
    # --- Detectar declaración ---
    if linea_de_lexemas and linea_de_lexemas[0] in TIPOS.keys():  
      # después del tipo vienen los identificadores, separados por coma
      ids = [x.strip().strip(",") for x in linea_de_lexemas[1:] if x != ","]

      for identificador in ids:
        if identificador in identificadores_declarados:
          # Declaración duplicada
          token = f"ED{token_error_declaracion}"
          token_error_declaracion += 1
          descripcion = f"Error de declaración duplicada: El lexema ya fue declarado"
          linea_error = lineas_recorridas + 1
          tabla_dicc.insert("", "end", values=(token, linea_error, identificador, descripcion))
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
          
          # Verificar si es un identificador (variable)
          es_variable = re.match(ID_REGEX, str(lexema_error))
          
          if not any(op in linea_de_lexemas for op in ["+","-","*","/"]):
            token = f"EA{token_error_asignacion}"
            token_error_asignacion += 1
            if es_variable:
              descripcion = "Error de asignación: Variable no declarada"
            else:
              descripcion = "Error de asignación: Lexema indeterminado"
          else:
            token = f"EO{token_error_operacion}"
            token_error_operacion += 1
            if es_variable:
              descripcion = "Error de operación: Variable no declarada"
            else:
              descripcion = "Error de operación: Lexema indeterminado"
          tabla_dicc.insert("", "end", values=(token, linea_error, lexema_error, descripcion))
          autoajustar_columnas(tabla_dicc)
      else:
        if not any(all(x in ('', tipo) for x in linea_de_tipos) for tipo in TIPOS):
          linea_error = lineas_recorridas + 1
          # Determinar tipo esperado (el más común en la línea, ignorando vacíos)
          tipos_validos = [t for t in linea_de_tipos if t not in ('', None)]
          tipo_esperado = max(set(tipos_validos), key=tipos_validos.count) if tipos_validos else None

          # Buscar el primer lexema que no coincida con el tipo esperado
          lexema_error = None
          for lexema, tipo_detectado in zip(linea_de_lexemas, linea_de_tipos):
            if tipo_detectado not in ('', None) and tipo_detectado != tipo_esperado:
              lexema_error = lexema
              break
          token = f"ET{token_error_tipo}"
          token_error_tipo += 1
          descripcion = f"Error de tipo: Incompatiblidad de tipos, {tipo_esperado}"
          tabla_dicc.insert("", "end", values=(token, linea_error, lexema_error, descripcion))
          autoajustar_columnas(tabla_dicc)
    lineas_recorridas += 1

def compilar_triplos(editor, tabla_triplos):
  """Genera y muestra la tabla de triplos"""
  codigo = editor.get("1.0", "end").strip()
  
  # Generar triplos
  triplos = generar_triplos(codigo)
  
  # Limpiar tabla
  for item in tabla_triplos.get_children():
    tabla_triplos.delete(item)
  
  # Insertar triplos en la tabla
  for no_linea, triplo in triplos.items():
    tabla_triplos.insert("", "end", values=(
      no_linea, 
      triplo['operador'], 
      triplo['Dato Objeto'], 
      triplo['Dato Fuente']
    ))
  
  autoajustar_columnas(tabla_triplos)
