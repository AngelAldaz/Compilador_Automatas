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

def actualizar_lineas(editor, lineas_text):
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