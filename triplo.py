def tokenizar_linea(linea):
    """
    Divide una línea en tokens, respetando strings entre comillas.
    """
    tokens = []
    i = 0
    token_actual = ""
    en_string = False
    
    while i < len(linea):
        char = linea[i]
        
        if char == '"':
            if en_string:
                token_actual += char
                tokens.append(token_actual)
                token_actual = ""
                en_string = False
            else:
                if token_actual:
                    tokens.append(token_actual)
                    token_actual = ""
                en_string = True
                token_actual += char
        elif en_string:
            token_actual += char
        elif char in ' \t':
            if token_actual:
                tokens.append(token_actual)
                token_actual = ""
        else:
            token_actual += char
        
        i += 1
    
    if token_actual:
        tokens.append(token_actual)
    
    return tokens

def es_evaluacion(linea_lexemas, listaEvaluacion = ["<",">","<=",">=","==","!=","="]):
    return any(op in linea_lexemas for op in listaEvaluacion)
def es_binario(linea_lexemas, listaBinarios = ["or","and"]):
    return any(op in linea_lexemas for op in listaBinarios)

def procesar_condicion_logica(evaluacion, tabla_triplos, contador_lineas, temp_counter, available_temporales):
    """
    Procesa expresiones lógicas con múltiples operadores AND/OR
    Respeta la precedencia: AND tiene mayor precedencia que OR
    Retorna: (contador_lineas actualizado, temp_counter actualizado, 
              linea_verdadero_final, linea_falso_final, linea_inicio)
    """
    # Primero, dividir por OR (menor precedencia)
    # Buscar todos los OR
    or_indices = [i for i, token in enumerate(evaluacion) if token == "or"]
    
    if or_indices:
        # Tenemos al menos un OR, procesar cada término separado por OR
        # Para OR: si cualquier término es verdadero, saltar al cuerpo
        # Solo si todos son falsos, salir del for
        
        linea_inicio = contador_lineas
        terminos = []
        ultimo_idx = 0
        
        for or_idx in or_indices:
            terminos.append(evaluacion[ultimo_idx:or_idx])
            ultimo_idx = or_idx + 1
        terminos.append(evaluacion[ultimo_idx:])  # último término
        
        lineas_verdadero_or = []
        linea_falso_final = None
        
        for idx, termino in enumerate(terminos):
            if "and" in termino:
                # Este término tiene ANDs, procesarlo recursivamente
                linea_inicio_termino = contador_lineas
                contador_lineas, temp_counter, _, linea_falso_termino, _ = procesar_condicion_logica(
                    termino, tabla_triplos, contador_lineas, temp_counter, available_temporales
                )
                # Si este término AND es falso, evaluar el siguiente término OR
                if idx < len(terminos) - 1:
                    # No es el último término, continuar con el siguiente
                    tabla_triplos[linea_falso_termino]["Dato Fuente"] = contador_lineas
                else:
                    # Es el último término, si es falso, salir del for
                    linea_falso_final = linea_falso_termino
            else:
                # Término simple (una sola comparación)
                temp, temp_counter = nuevo_temporal(temp_counter, available_temporales)
                contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "=", temp, termino[0], available_temporales)
                contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, termino[1], temp, termino[2], available_temporales)
                
                # Si es verdadero, ir al cuerpo del for
                linea_verdadero = contador_lineas
                lineas_verdadero_or.append(linea_verdadero)
                contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "Verdadero", "", "Pendiente_OR", available_temporales)
                
                if idx < len(terminos) - 1:
                    # Si es falso, evaluar el siguiente término
                    contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "Falso", "", contador_lineas + 1, available_temporales)
                else:
                    # Es el último término, si es falso, salir del for
                    linea_falso_final = contador_lineas
                    contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "Falso", "", "Pendiente_FINAL", available_temporales)
        
        # Actualizar todos los saltos de verdadero al inicio del cuerpo del for
        linea_cuerpo = contador_lineas
        for linea_v in lineas_verdadero_or:
            if linea_v in tabla_triplos:
                tabla_triplos[linea_v]["Dato Fuente"] = linea_cuerpo
        
        return contador_lineas, temp_counter, lineas_verdadero_or, linea_falso_final, linea_inicio
    
    else:
        # No hay OR, pero puede haber múltiples ANDs
        and_indices = [i for i, token in enumerate(evaluacion) if token == "and"]
        
        if and_indices:
            # Tenemos múltiples ANDs
            # Para AND: todas las condiciones deben ser verdaderas
            # Si cualquiera es falsa, salir del for
            
            linea_inicio = contador_lineas
            terminos = []
            ultimo_idx = 0
            
            for and_idx in and_indices:
                terminos.append(evaluacion[ultimo_idx:and_idx])
                ultimo_idx = and_idx + 1
            terminos.append(evaluacion[ultimo_idx:])  # último término
            
            linea_falso_final = None
            lineas_falso_and = []
            
            for idx, termino in enumerate(terminos):
                # Evaluar cada término
                temp, temp_counter = nuevo_temporal(temp_counter, available_temporales)
                contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "=", temp, termino[0], available_temporales)
                contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, termino[1], temp, termino[2], available_temporales)
                
                if idx < len(terminos) - 1:
                    # No es el último término
                    # Si es verdadero, evaluar el siguiente
                    contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "Verdadero", "", contador_lineas + 2, available_temporales)
                    # Si es falso, salir del for
                    linea_falso = contador_lineas
                    lineas_falso_and.append(linea_falso)
                    contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "Falso", "", "Pendiente_AND_F", available_temporales)
                else:
                    # Es el último término
                    # Si es verdadero, ir al cuerpo del for
                    contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "Verdadero", "", contador_lineas + 2, available_temporales)
                    # Si es falso, salir del for
                    linea_falso_final = contador_lineas
                    contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "Falso", "", "Pendiente_FINAL", available_temporales)
            
            # Actualizar todos los saltos de falso al mismo punto (salida del for)
            for linea_f in lineas_falso_and:
                tabla_triplos[linea_f]["Dato Fuente"] = linea_falso_final
            
            return contador_lineas, temp_counter, None, linea_falso_final, linea_inicio
        
        else:
            # Condición simple (sin AND ni OR)
            linea_inicio = contador_lineas
            temp, temp_counter = nuevo_temporal(temp_counter, available_temporales)
            contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "=", temp, evaluacion[0], available_temporales)
            contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, evaluacion[1], temp, evaluacion[2], available_temporales)
            
            # Verdadero: ir al cuerpo
            contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "Verdadero", "", contador_lineas + 2, available_temporales)
            # Falso: salir del for
            linea_falso_final = contador_lineas
            contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "Falso", "", "Pendiente_FINAL", available_temporales)
            
            return contador_lineas, temp_counter, None, linea_falso_final, linea_inicio
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
    """
    Reduce expresiones respetando la jerarquía de operadores:
    1. Multiplicación (*), División (/) y Módulo (%) - Mayor precedencia
    2. Suma (+) y Resta (-) - Menor precedencia
    """
    if len(tokens) == 1:
        return tokens[0], contador_lineas, temp_counter
    
    # Primero, procesar multiplicaciones, divisiones y módulos (mayor precedencia)
    # Buscar operadores *, /, % de izquierda a derecha
    i = 1
    while i < len(tokens):
        if i < len(tokens) and tokens[i] in ['*', '/', '%']:
            # Encontramos una multiplicación, división o módulo
            operando_izq = tokens[i-1]
            operador = tokens[i]
            operando_der = tokens[i+1]
            
            # Crear temporal para este resultado
            temp, temp_counter = nuevo_temporal(temp_counter, available_temporales)
            
            # Si el operando izquierdo no es temporal, asignarlo primero
            if not (isinstance(operando_izq, str) and operando_izq.startswith("T")):
                contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "=", temp, operando_izq, available_temporales)
                contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, operador, temp, operando_der, available_temporales)
            else:
                # El operando izquierdo ya es temporal, reutilizarlo
                contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, operador, operando_izq, operando_der, available_temporales)
                temp = operando_izq
            
            # Reemplazar los 3 tokens (operando_izq op operando_der) con el temporal
            tokens = tokens[:i-1] + [temp] + tokens[i+2:]
            # No incrementar i, revisar desde la misma posición
        else:
            i += 2  # Saltar al siguiente operador
    
    # Ahora solo quedan sumas y restas (o un solo operando)
    if len(tokens) == 1:
        return tokens[0], contador_lineas, temp_counter
    
    # Procesar sumas y restas de izquierda a derecha
    # Si el primer operando es temporal, reutilizarlo
    if isinstance(tokens[0], str) and tokens[0].startswith("T"):
        temp = tokens[0]
        i = 1
        while i < len(tokens):
            op = tokens[i]
            rhs = tokens[i+1]
            contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, op, temp, rhs, available_temporales)
            i += 2
        return temp, contador_lineas, temp_counter
    else:
        # Crear nuevo temporal
        temp, temp_counter = nuevo_temporal(temp_counter, available_temporales)
        contador_lineas = emitir_triplo(tabla_triplos, contador_lineas, "=", temp, tokens[0], available_temporales)
        # Aplicar cada operador sobre el temporal
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
        linea_lexemas = tokenizar_linea(linea)
        
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
                        
                        # Procesar la condición (simple o compleja con AND/OR)
                        contador_lineas, temp_counter, _, false_triple_key, linea_inicio_for = procesar_condicion_logica(
                            evaluacion, tabla_triplos, contador_lineas, temp_counter, available_temporales
                        )
                        
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

if __name__ == "__main__":
    # Prueba original
    print("=" * 60)
    print("PRUEBA 1: Condición simple")
    print("=" * 60)
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
    
    # Prueba con AND
    print("\n" + "=" * 60)
    print("PRUEBA 2: Condición con AND")
    print("=" * 60)
    lineaUno_and = "for id_int1 < 5 and id_int2 > 3 ; id_int1 = id_int1 + 1 {"
    lineaDos_and = "id_int2 = id_int3 + 1"
    lineaTres_and = "}"
    codigo_prueba_and = "\n".join([lineaUno_and, lineaDos_and, lineaTres_and])
    
    tabla_triplos_and = generar_triplos(codigo_prueba_and)
    
    for linea in codigo_prueba_and.split("\n"):
        print(linea)
    print("\nNo. Línea\tOperador\tDato Objeto\tDato Fuente")
    print("-----------------------------------------------------")
    for no_linea, triplo in tabla_triplos_and.items():
        print(f"{no_linea}\t\t{triplo['operador']}\t\t{triplo['Dato Objeto']}\t\t{triplo['Dato Fuente']}")
    
    # Prueba con OR
    print("\n" + "=" * 60)
    print("PRUEBA 3: Condición con OR")
    print("=" * 60)
    lineaUno_or = "for id_int1 < 5 or id_int2 > 3 ; id_int1 = id_int1 + 1 {"
    lineaDos_or = "id_int2 = id_int3 + 1"
    lineaTres_or = "}"
    codigo_prueba_or = "\n".join([lineaUno_or, lineaDos_or, lineaTres_or])
    
    tabla_triplos_or = generar_triplos(codigo_prueba_or)
    
    for linea in codigo_prueba_or.split("\n"):
        print(linea)
    print("\nNo. Línea\tOperador\tDato Objeto\tDato Fuente")
    print("-----------------------------------------------------")
    for no_linea, triplo in tabla_triplos_or.items():
        print(f"{no_linea}\t\t{triplo['operador']}\t\t{triplo['Dato Objeto']}\t\t{triplo['Dato Fuente']}")
    
    # Prueba con múltiples AND
    print("\n" + "=" * 60)
    print("PRUEBA 4: Múltiples AND")
    print("=" * 60)
    lineaUno_multi_and = "for id_int1 < 5 and id_int2 > 3 and id_int3 < 10 ; id_int1 = id_int1 + 1 {"
    lineaDos_multi_and = "id_int2 = id_int3 + 1"
    lineaTres_multi_and = "}"
    codigo_prueba_multi_and = "\n".join([lineaUno_multi_and, lineaDos_multi_and, lineaTres_multi_and])
    
    tabla_triplos_multi_and = generar_triplos(codigo_prueba_multi_and)
    
    for linea in codigo_prueba_multi_and.split("\n"):
        print(linea)
    print("\nNo. Línea\tOperador\tDato Objeto\tDato Fuente")
    print("-----------------------------------------------------")
    for no_linea, triplo in tabla_triplos_multi_and.items():
        print(f"{no_linea}\t\t{triplo['operador']}\t\t{triplo['Dato Objeto']}\t\t{triplo['Dato Fuente']}")
    
    # Prueba con múltiples OR
    print("\n" + "=" * 60)
    print("PRUEBA 5: Múltiples OR")
    print("=" * 60)
    lineaUno_multi_or = "for id_int1 < 5 or id_int2 > 3 or id_int3 < 10 ; id_int1 = id_int1 + 1 {"
    lineaDos_multi_or = "id_int2 = id_int3 + 1"
    lineaTres_multi_or = "}"
    codigo_prueba_multi_or = "\n".join([lineaUno_multi_or, lineaDos_multi_or, lineaTres_multi_or])
    
    tabla_triplos_multi_or = generar_triplos(codigo_prueba_multi_or)
    
    for linea in codigo_prueba_multi_or.split("\n"):
        print(linea)
    print("\nNo. Línea\tOperador\tDato Objeto\tDato Fuente")
    print("-----------------------------------------------------")
    for no_linea, triplo in tabla_triplos_multi_or.items():
        print(f"{no_linea}\t\t{triplo['operador']}\t\t{triplo['Dato Objeto']}\t\t{triplo['Dato Fuente']}")
    
    # Prueba con mezcla de AND y OR
    print("\n" + "=" * 60)
    print("PRUEBA 6: Mezcla AND y OR (precedencia)")
    print("=" * 60)
    lineaUno_mix = "for id_int1 < 5 or id_int2 > 3 and id_int3 < 10 ; id_int1 = id_int1 + 1 {"
    lineaDos_mix = "id_int2 = id_int3 + 1"
    lineaTres_mix = "}"
    codigo_prueba_mix = "\n".join([lineaUno_mix, lineaDos_mix, lineaTres_mix])
    
    tabla_triplos_mix = generar_triplos(codigo_prueba_mix)
    
    for linea in codigo_prueba_mix.split("\n"):
        print(linea)
    print("\nNo. Línea\tOperador\tDato Objeto\tDato Fuente")
    print("-----------------------------------------------------")
    for no_linea, triplo in tabla_triplos_mix.items():
        print(f"{no_linea}\t\t{triplo['operador']}\t\t{triplo['Dato Objeto']}\t\t{triplo['Dato Fuente']}")
