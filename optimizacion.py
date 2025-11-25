"""
Módulo para detectar optimizaciones en el código
Técnica: Eliminación de Código Redundante
"""
import re
from config import ID_REGEX

def detectar_optimizaciones(codigo):
    """
    Detecta instrucciones redundantes en el código
    Retorna: lista de números de línea que pueden ser optimizadas
    """
    lineas = codigo.strip().split('\n')
    lineas_optimizables = []
    
    # Diccionario para rastrear última asignación de cada combinación variable=expresion
    # Formato: {clave_asignacion: (num_linea, variables_en_expresion)}
    ultimas_asignaciones = {}
    
    # Diccionario para rastrear en qué línea fue modificada cada variable por última vez
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
                
                # Verificar si es un identificador válido
                if re.match(ID_REGEX, variable):
                    # Extraer todas las variables usadas en la expresión
                    variables_en_expresion = set(re.findall(ID_REGEX, expresion))
                    
                    # Crear una clave única para esta asignación
                    clave_asignacion = f"{variable}={expresion}"
                    
                    # Verificar si esta misma asignación ya existe
                    if clave_asignacion in ultimas_asignaciones:
                        linea_anterior, vars_anteriores = ultimas_asignaciones[clave_asignacion]
                        
                        # Verificar si ALGUNA de las variables en la expresión fue modificada
                        # después de la última vez que se hizo esta asignación
                        alguna_var_cambio = False
                        for var in variables_en_expresion:
                            if var in ultima_modificacion:
                                if ultima_modificacion[var] > linea_anterior:
                                    alguna_var_cambio = True
                                    break
                        
                        if not alguna_var_cambio:
                            # Ninguna variable cambió, esta línea es redundante
                            lineas_optimizables.append(num_linea)
                        else:
                            # Al menos una variable cambió, actualizar la asignación
                            ultimas_asignaciones[clave_asignacion] = (num_linea, variables_en_expresion)
                    else:
                        # Primera vez que vemos esta asignación
                        ultimas_asignaciones[clave_asignacion] = (num_linea, variables_en_expresion)
                    
                    # Registrar que esta variable fue modificada en esta línea
                    ultima_modificacion[variable] = num_linea
                    
                    # Limpiar asignaciones anteriores de esta misma variable (con otras expresiones)
                    claves_a_eliminar = [k for k in ultimas_asignaciones.keys() 
                                        if k.startswith(f"{variable}=") and k != clave_asignacion]
                    for k in claves_a_eliminar:
                        del ultimas_asignaciones[k]
        
        # Manejar FOR loops
        if 'for' in lexemas and ';' in lexemas:
            idx_puntocoma = lexemas.index(';')
            if idx_puntocoma + 1 < len(lexemas):
                var_modificada = lexemas[idx_puntocoma + 1]
                # Registrar modificación
                ultima_modificacion[var_modificada] = num_linea
                # Limpiar asignaciones de esta variable
                claves_a_eliminar = [k for k in ultimas_asignaciones.keys() 
                                    if k.startswith(f"{var_modificada}=")]
                for k in claves_a_eliminar:
                    del ultimas_asignaciones[k]
    
    return lineas_optimizables


def aplicar_optimizacion(codigo):
    """
    Aplica la optimización eliminando líneas redundantes
    Retorna: (codigo_optimizado, lineas_eliminadas)
    """
    lineas = codigo.strip().split('\n')
    lineas_optimizables = detectar_optimizaciones(codigo)
    
    codigo_optimizado = []
    for i, linea in enumerate(lineas):
        num_linea = i + 1
        if num_linea not in lineas_optimizables:
            codigo_optimizado.append(linea)
    
    return '\n'.join(codigo_optimizado), lineas_optimizables


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
