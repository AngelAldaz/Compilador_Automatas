# Expresión regular para los identificadores
ID_REGEX = r"id_[A-Za-z0-9_-]+"
REGEX_STRING = r'"([^"]+)"'

# Tipos de datos
# tipos = ["num", "chain", "cow"]
TIPOS = {"num": "int", "chain": "str", "cow": "float"}

# Texto inicial en el editor
TEXTO_INICIAL ="""num id_a , id_b , id_c , id_w , id_j , id_m
cow id_real1 , id_real2
chain id_cadena1 , id_cadena2
id_a = id_j + 56
id_b = id_m - 45
id_c = id_j + 56
id_w = id_a + id_b
id_b = id_c * 4
id_real1 = 3
id_real2 = id_real1 * 2
id_real2 = id_real1 * 2
for id_a < 5 ; id_a = id_a + 1 {
id_w = id_w + 1
}
"""