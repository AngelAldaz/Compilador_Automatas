def es_evaluacion(linea_lexemas, listaEvaluacion = ["<",">","<=",">=","==","!=","="]):
    return any(op in linea_lexemas for op in listaEvaluacion)
def es_binario(linea_lexemas, listaBinarios = ["or","and"]):
    return any(op in linea_lexemas for op in listaBinarios)
def contenidoParentesis(linea_lexemas):
  # Revisar jerarquia de operaciones ej ["(", "id_int3", "+", "1", ")", "*", "3"]
  sublista = ""
  for i in range(len(linea_lexemas)):
    if linea_lexemas[i] == "(":
      # buscar cierre
      for j in range(i + 1, len(linea_lexemas)):
        if linea_lexemas[j] == ")":
          # extraer sublista
          sublista = linea_lexemas[i + 1:j]
          # print("Sublista encontrada:", sublista)
          # procesar sublista recursivamente
          contenidoParentesis(sublista)
          break
  # retornar linea_lexemas procesada
  return sublista

def triplo(linea_lexemas):
  # Procesar linea_lexemas para generar triplo
  # Ejemplo: ["id_int2", "=", "(", "id_int3", "+", "1", ")", "*", "3"]
  # Identificar operador principal (fuera de paréntesis)
  operador_principal = ""
  dato_objeto = ""
  dato_fuente = ""
  for i in range(len(linea_lexemas)):
    if linea_lexemas[i] in ["+", "-", "*", "/"] and linea_lexemas[i-1] != "(" and linea_lexemas[i+1] != ")":
      operador_principal = linea_lexemas[i]
      break
  # Generar triplo basado en el operador principal
  if operador_principal:
    indice_op = linea_lexemas.index(operador_principal)
    dato_objeto = linea_lexemas[indice_op - 1]
    dato_fuente = linea_lexemas[indice_op + 1]
    # print(f"Triplo generado: ({operador_principal}, {dato_objeto}, {dato_fuente})")
  return operador_principal, dato_objeto, dato_fuente
  # else:
    # print("No se encontró un operador principal en la línea.")

# Helper para emitir triplos y mantener la piscina de temporales reutilizables
def emitir_triplo(tabla_triplos, contador_lineas, operador, dato_objeto, dato_fuente, available_temporales):
    tabla_triplos[contador_lineas] = {"operador": operador, "Dato Objeto": dato_objeto, "Dato Fuente": dato_fuente}
    # si la fuente es temporal, añadirla a la piscina (puede reutilizarse)
    if isinstance(dato_fuente, str) and dato_fuente.startswith("T"):
        if dato_fuente not in available_temporales:
            available_temporales.append(dato_fuente)
    # si el objeto es temporal, se está re-asignando: quitarlo de la piscina
    if isinstance(dato_objeto, str) and dato_objeto.startswith("T"):
        if dato_objeto in available_temporales:
            available_temporales.remove(dato_objeto)
    return contador_lineas + 1

# Nuevas funciones para reducir expresiones usando temporales y piscina de reutilizables
def nuevo_temporal(temp_counter, available_temporales):
    # Reusar un temporal disponible si existe, sino crear uno nuevo
    if available_temporales:
        return available_temporales.pop(0), temp_counter
    nombre = f"T{temp_counter}"
    return nombre, temp_counter + 1

def reducir_expresion_flat(tokens, tabla_triplos, contador_lineas, temp_counter, available_temporales):
    # tokens es una lista sin paréntesis: ej ["id_int3","+","1","*","3"] (se reduce left-to-right)
    if len(tokens) == 1:
        return tokens[0], contador_lineas, temp_counter
    # Si el primer operando ya es un temporal, reutilizarlo (no crear otro temporal)
    first = tokens[0]
    if isinstance(first, str) and first.startswith("T"):
        temp = first
        i = 1
        while i < len(tokens):
            op = tokens[i]
            rhs = tokens[i+1]
            contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, op, temp, rhs, available_temporales)
            i += 2
        return temp, contador_lineas, temp_counter
    # iniciar temporal: reusar si hay disponible o crear nuevo
    temp, temp_counter = nuevo_temporal(temp_counter, available_temporales)
    contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "=", temp, tokens[0], available_temporales)
    # aplicar cada operador sobre el temporal
    i = 1
    while i < len(tokens):
        op = tokens[i]
        rhs = tokens[i+1]
        contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, op, temp, rhs, available_temporales)
        i += 2
    return temp, contador_lineas, temp_counter

def procesar_expresion(tokens, tabla_triplos, contador_lineas, temp_counter, available_temporales):
    # Reduce paréntesis de adentro hacia afuera
    while "(" in tokens:
        # buscar '(' más interno
        last_open = max(i for i,t in enumerate(tokens) if t == "(")
        # buscar su cierre correspondiente
        close = None
        for j in range(last_open+1, len(tokens)):
            if tokens[j] == ")":
                close = j
                break
        if close is None:
            break  # paréntesis no balanceados
        sub = tokens[last_open+1:close]
        resultado_sub, contador_lineas, temp_counter = reducir_expresion_flat(sub, tabla_triplos, contador_lineas, temp_counter, available_temporales)
        # reemplazar ( ... ) por el nombre del temporal/resultado
        tokens = tokens[:last_open] + [resultado_sub] + tokens[close+1:]
    # ya sin paréntesis, reducir la expresión completa
    resultado, contador_lineas, temp_counter = reducir_expresion_flat(tokens, tabla_triplos, contador_lineas, temp_counter, available_temporales)
    return resultado, contador_lineas, temp_counter

def generar_triplos(codigo):
    """Genera la tabla de triplos a partir del código fuente"""
    lineas = codigo.strip().split("\n")
    contador_lineas = 1
    tabla_triplos = {}
    operacion = ""
    linea_inicio_for = 0
    linea_fin_for = 0
    temp_counter = 1
    available_temporales = []
    false_triple_key = None
    
    for linea in lineas:
        linea_lexemas = linea.split()
        
        if linea.strip() == "}":
            # antes de actualizar el triplo Falso, generar el incremento y el JMP al inicio del for
            if operacion:
                # operacion ejemplo: ['id_int1','=', 'id_int1','+','1']
                lhs = operacion[0]
                if "=" in operacion:
                    # rhs tokens después del '='
                    try:
                        idx_eq = operacion.index("=")
                        rhs_tokens = operacion[idx_eq+1:]
                    except ValueError:
                        rhs_tokens = operacion[1:]
                else:
                    rhs_tokens = operacion[1:]
                # generar temporales y asignación del incremento
                resultado, contador_lineas, temp_counter = procesar_expresion(rhs_tokens, tabla_triplos, contador_lineas, temp_counter, available_temporales)
                contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "=", lhs, resultado, available_temporales)
                # generar JMP al inicio del for
                contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "JMP", "", linea_inicio_for, available_temporales)
            # ahora la línea de fin del for es la siguiente instrucción disponible
            linea_fin_for = contador_lineas
            # si ya existe el triplo Falso, actualizar su "Dato Fuente" con la línea de fin
            if false_triple_key is not None:
                tabla_triplos[false_triple_key]["Dato Fuente"] = linea_fin_for
                
        if es_evaluacion(linea_lexemas):
            variables_temporales = {}
            if linea_lexemas[0] == "for":
                for j in range(1, len(linea_lexemas)):
                    if linea_lexemas[j] == ";":
                        evaluacion = linea_lexemas[1:j]
                        if not es_binario(evaluacion):
                            # crear variable temporal para la evaluación
                            variables_temporales['T1'] = evaluacion[0]
                            contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "=", "T1", variables_temporales['T1'], available_temporales)
                            linea_inicio_for = contador_lineas - 1
                            contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, evaluacion[1], "T1", evaluacion[2], available_temporales)
                            # fijar Verdadero al inicio del cuerpo
                            contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "Verdadero", "", contador_lineas + 2, available_temporales)
                            # guardar la clave del triplo Falso para actualizarla luego
                            false_triple_key = contador_lineas
                            contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "Falso", "", "Siguiente", available_temporales)
                        # extraer la operación de incremento (entre ';' y '{')
                        for k in range(j + 1, len(linea_lexemas)):
                            if linea_lexemas[k] == "{":
                                operacion = linea_lexemas[j+1:k]
                                break
                        break
            else:
                # si es una asignación, separar lado izquierdo y derecho
                if "=" in linea_lexemas:
                    idx_eq = linea_lexemas.index("=")
                    lhs = linea_lexemas[0]
                    rhs_tokens = linea_lexemas[idx_eq+1:]
                    resultado, contador_lineas, temp_counter = procesar_expresion(rhs_tokens, tabla_triplos, contador_lineas, temp_counter, available_temporales)
                    # asignar resultado al lhs
                    contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "=", lhs, resultado, available_temporales)
                else:
                    # líneas que no son asignaciones directas
                    resultado, contador_lineas, temp_counter = procesar_expresion(linea_lexemas, tabla_triplos, contador_lineas, temp_counter, available_temporales)
    
    return tabla_triplos

# ============ CÓDIGO DE PRUEBA (solo se ejecuta si se corre directamente) ============
if __name__ == "__main__":
    lineaUno = "for id_int1 < 5 ; id_int1 = id_int1 + 1 {"
    lineaDos = "id_int2 = ( id_int3 + 1 ) * 3"
    lineaTres = "id_int3 = id_int3  * ( 2 + 4 )"
    lineaCuatro =  "}"
    lineaCinco = "id_int3 = 0"
    codigo_prueba = "\n".join([lineaUno, lineaDos, lineaTres, lineaCuatro, lineaCinco])
    
    # Generar triplos usando la función principal
    tabla_triplos = generar_triplos(codigo_prueba)
    
    # Imprimir resultados
    for linea in codigo_prueba.split("\n"):
        print(linea)
    print("\nNo. Línea\tOperador\tDato Objeto\tDato Fuente")
    print("-----------------------------------------------------")
    for no_linea, triplo in tabla_triplos.items():
        print(f"{no_linea}\t\t{triplo['operador']}\t\t{triplo['Dato Objeto']}\t\t{triplo['Dato Fuente']}")
