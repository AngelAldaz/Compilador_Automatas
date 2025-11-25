# Expresión regular para los identificadores
ID_REGEX = r"id_[A-Za-z0-9_-]+"
REGEX_STRING = r'"([^"]+)"'

# Tipos de datos
# tipos = ["num", "chain", "cow"]
TIPOS = {"num": "int", "chain": "str", "cow": "float"}

# Texto inicial en el editor
TEXTO_INICIAL ="""num id_int1 , id_int2 , id_int3
cow id_real1 , id_real2 , id_real3
chain id_cadena1 , id_cadena2 , id_cadena3
id_int1 = id_int2 + 5
id_int2 = id_int3 + 10
id_int1 = id_int2 + 5
id_int2 = id_int3 + 10
id_real1 = 3
id_real2 = id_real1 * 2
id_real2 = id_real1 * 2
for id_int1 < 5 ; id_int1 = id_int1 + 1 {
id_int3 = id_int2 + 1
}
id_int3 = 0
"""