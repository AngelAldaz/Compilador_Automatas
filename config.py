import re

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