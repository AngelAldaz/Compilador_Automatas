"""
Módulo para detectar optimizaciones en el código
Técnica: Eliminación de Código Redundante
"""
import re
from config import ID_REGEX

def detectar_optimizaciones(codigo):
    """
    Detecta instrucciones redundantes en el código usando la misma lógica que aplicar_optimizacion
    Retorna: lista de números de línea que pueden ser optimizadas
    """
    lineas = codigo.strip().split('\n')
    lineas_optimizables = []
    
    # Diccionario: expresion -> variable que la contiene
    expresion_a_variable = {}
    
    # Diccionario para rastrear última modificación
    ultima_modificacion = {}
    
    for i, linea in enumerate(lineas):
        num_linea = i + 1
        lexemas = linea.split()
        
        # Buscar asignaciones: variable = expresion
        if '=' in lexemas and lexemas[0] != 'for':
            idx_igual = lexemas.index('=')
            if idx_igual > 0:
                variable = lexemas[0]
                expresion = ' '.join(lexemas[idx_igual + 1:])
                
                if re.match(ID_REGEX, variable):
                    # Extraer variables usadas en la expresión
                    variables_en_expresion = set(re.findall(ID_REGEX, expresion))
                    
                    # Verificar si esta expresión ya fue calculada antes
                    if expresion in expresion_a_variable:
                        var_anterior = expresion_a_variable[expresion]
                        
                        # Verificar si alguna variable en la expresión cambió
                        alguna_var_cambio = False
                        for var in variables_en_expresion:
                            if var in ultima_modificacion:
                                # Buscar la ÚLTIMA línea donde se asignó var_anterior (antes de la actual)
                                linea_var_anterior = None
                                for j in range(i):
                                    linea_previa = lineas[j].split()
                                    if linea_previa and linea_previa[0] == var_anterior:
                                        linea_var_anterior = j + 1
                                
                                # Comparar si la variable cambió después de esa asignación
                                if linea_var_anterior and ultima_modificacion[var] > linea_var_anterior:
                                    alguna_var_cambio = True
                                    break
                        
                        if not alguna_var_cambio:
                            # Esta línea es redundante
                            lineas_optimizables.append(num_linea)
                            continue
                    
                    # Registrar esta expresión
                    expresion_a_variable[expresion] = variable
                    
                    # NO limpiar expresiones de la misma variable - necesitamos detectar redundancias consecutivas
                    # Solo registrar la modificación
                    
                    # Registrar modificación
                    ultima_modificacion[variable] = num_linea
        
        # Manejar FOR loops
        elif 'for' in lexemas and ';' in lexemas:
            idx_puntocoma = lexemas.index(';')
            if idx_puntocoma + 1 < len(lexemas):
                var_modificada = lexemas[idx_puntocoma + 1]
                ultima_modificacion[var_modificada] = num_linea
                # Limpiar expresiones con esta variable
                expresiones_a_eliminar = [exp for exp, var in expresion_a_variable.items() 
                                         if var == var_modificada or var_modificada in exp]
                for exp in expresiones_a_eliminar:
                    del expresion_a_variable[exp]
    
    return lineas_optimizables


def aplicar_optimizacion(codigo):
    """
    Aplica la optimización eliminando líneas redundantes y sustituyendo variables
    Retorna: (codigo_optimizado, lineas_eliminadas, lineas_modificadas)
    """
    lineas = codigo.strip().split('\n')
    lineas_optimizables = []
    lineas_modificadas = []  # Líneas que tienen sustituciones
    
    # Diccionario: expresion -> variable que la contiene
    expresion_a_variable = {}
    
    # Diccionario: variable -> variable equivalente (para sustituciones)
    variable_equivalente = {}
    
    # Diccionario para rastrear última modificación
    ultima_modificacion = {}
    
    codigo_optimizado = []
    
    for i, linea in enumerate(lineas):
        num_linea = i + 1
        lexemas = linea.split()
        
        # Buscar asignaciones: variable = expresion
        if '=' in lexemas and lexemas[0] != 'for':
            idx_igual = lexemas.index('=')
            if idx_igual > 0:
                variable = lexemas[0]
                expresion = ' '.join(lexemas[idx_igual + 1:])
                
                if re.match(ID_REGEX, variable):
                    # Sustituir variables en la expresión por sus equivalentes
                    expresion_sustituida = expresion
                    for var_original, var_equivalente in variable_equivalente.items():
                        expresion_sustituida = re.sub(r'\b' + re.escape(var_original) + r'\b', 
                                                     var_equivalente, 
                                                     expresion_sustituida)
                    
                    # Extraer variables usadas en la expresión
                    variables_en_expresion = set(re.findall(ID_REGEX, expresion_sustituida))
                    
                    # Verificar si esta expresión ya fue calculada antes
                    if expresion_sustituida in expresion_a_variable:
                        var_anterior = expresion_a_variable[expresion_sustituida]
                        
                        # Verificar si alguna variable en la expresión cambió
                        alguna_var_cambio = False
                        for var in variables_en_expresion:
                            if var in ultima_modificacion:
                                # Buscar la ÚLTIMA línea donde se asignó var_anterior (antes de la actual)
                                linea_var_anterior = None
                                for j in range(i):
                                    linea_previa = lineas[j].split()
                                    if linea_previa and linea_previa[0] == var_anterior:
                                        linea_var_anterior = j + 1
                                
                                # Comparar si la variable cambió después de esa asignación
                                if linea_var_anterior and ultima_modificacion[var] > linea_var_anterior:
                                    alguna_var_cambio = True
                                    break
                        
                        if not alguna_var_cambio:
                            # Esta línea es redundante
                            lineas_optimizables.append(num_linea)
                            # Registrar que esta variable es equivalente a la anterior
                            variable_equivalente[variable] = var_anterior
                            continue  # No agregar esta línea al código optimizado
                    
                    # Agregar la línea (con sustituciones si las hay)
                    if expresion_sustituida != expresion:
                        linea_optimizada = f"{variable} = {expresion_sustituida}"
                        codigo_optimizado.append(linea_optimizada)
                        # Marcar esta línea como modificada
                        lineas_modificadas.append(num_linea)
                    else:
                        codigo_optimizado.append(linea)
                    
                    # Registrar esta expresión
                    expresion_a_variable[expresion_sustituida] = variable
                    
                    # NO limpiar expresiones - mantener registro para detectar redundancias consecutivas
                    # Solo limpiar si la variable tiene una expresión DIFERENTE
                    # expresiones_a_eliminar = [exp for exp, var in expresion_a_variable.items() if var == variable and exp != expresion_sustituida]
                    # for exp in expresiones_a_eliminar:
                    #     del expresion_a_variable[exp]
                    
                    # Registrar modificación
                    ultima_modificacion[variable] = num_linea
                    
                    # Limpiar equivalencias que involucren esta variable
                    vars_a_limpiar = [v for v, eq in variable_equivalente.items() if eq == variable or v == variable]
                    for v in vars_a_limpiar:
                        del variable_equivalente[v]
        
        # Manejar FOR loops
        elif 'for' in lexemas and ';' in lexemas:
            codigo_optimizado.append(linea)
            idx_puntocoma = lexemas.index(';')
            if idx_puntocoma + 1 < len(lexemas):
                var_modificada = lexemas[idx_puntocoma + 1]
                ultima_modificacion[var_modificada] = num_linea
                # Limpiar expresiones con esta variable
                expresiones_a_eliminar = [exp for exp, var in expresion_a_variable.items() 
                                         if var == var_modificada or var_modificada in exp]
                for exp in expresiones_a_eliminar:
                    del expresion_a_variable[exp]
        else:
            # Otras líneas (declaraciones, llaves, etc.)
            codigo_optimizado.append(linea)
    
    return '\n'.join(codigo_optimizado), lineas_optimizables, lineas_modificadas


def obtener_estadisticas_optimizacion(codigo_original, codigo_optimizado, triplos_original, triplos_optimizado):
    """
    Calcula estadísticas de la optimización
    """
    lineas_originales = len(codigo_original.strip().split('\n'))
    lineas_optimizadas = len(codigo_optimizado.strip().split('\n'))
    lineas_eliminadas = lineas_originales - lineas_optimizadas
    
    porcentaje_reduccion_codigo = (lineas_eliminadas / lineas_originales * 100) if lineas_originales > 0 else 0
    
    triplos_eliminados = triplos_original - triplos_optimizado
    porcentaje_reduccion_triplos = (triplos_eliminados / triplos_original * 100) if triplos_original > 0 else 0
    
    return {
        'lineas_originales': lineas_originales,
        'lineas_optimizadas': lineas_optimizadas,
        'lineas_eliminadas': lineas_eliminadas,
        'porcentaje_reduccion_codigo': porcentaje_reduccion_codigo,
        'triplos_originales': triplos_original,
        'triplos_optimizados': triplos_optimizado,
        'triplos_eliminados': triplos_eliminados,
        'porcentaje_reduccion_triplos': porcentaje_reduccion_triplos
    }
