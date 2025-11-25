"""
Tokenizador que respeta strings entre comillas
"""
import re

def tokenizar_linea(linea):
    """
    Divide una línea en tokens, respetando strings entre comillas.
    Ejemplo: 'id_mensaje = "Fin del codigo"' -> ['id_mensaje', '=', '"Fin del codigo"']
    """
    tokens = []
    i = 0
    token_actual = ""
    en_string = False
    
    while i < len(linea):
        char = linea[i]
        
        if char == '"':
            if en_string:
                # Fin del string
                token_actual += char
                tokens.append(token_actual)
                token_actual = ""
                en_string = False
            else:
                # Inicio del string
                if token_actual:
                    tokens.append(token_actual)
                    token_actual = ""
                en_string = True
                token_actual += char
        elif en_string:
            # Dentro de un string, capturar todo
            token_actual += char
        elif char in ' \t':
            # Espacio fuera de string - separador
            if token_actual:
                tokens.append(token_actual)
                token_actual = ""
        else:
            # Carácter normal
            token_actual += char
        
        i += 1
    
    # Agregar último token si existe
    if token_actual:
        tokens.append(token_actual)
    
    return tokens

if __name__ == "__main__":
    # Pruebas
    tests = [
        'id_mensaje = "Fin del codigo"',
        'chain id_nombre , id_apellido',
        'id_completo = "Hola" + "Mundo"',
        'id_numero = 42',
        'for id_x < 10 ; id_x = id_x + 1 {',
    ]
    
    print("Pruebas del tokenizador:")
    print("=" * 60)
    for test in tests:
        tokens = tokenizar_linea(test)
        print(f"Entrada: {test}")
        print(f"Tokens:  {tokens}")
        print()
