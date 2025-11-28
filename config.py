# Expresión regular para los identificadores
ID_REGEX = r"id_[A-Za-z0-9_-]+"
REGEX_STRING = r'"([^"]+)"'

# Tipos de datos
# tipos = ["num", "chain", "cow"]
TIPOS = {"num": "int", "chain": "str", "cow": "float"}

# Texto inicial en el editor
TEXTO_INICIAL ="""num id_contador , id_suma , id_temp
cow id_precio , id_descuento , id_total
chain id_nombre , id_codigo , id_mensaje
id_contador = 0
id_suma = id_contador + 10 * 2
id_temp = id_contador + 10 * 2
id_precio = 100
id_descuento = id_precio - 15 / 2
id_total = id_precio - id_descuento
id_descuento = id_precio - 15 * 3
id_contador = 5
id_suma = id_contador + 10 / 10
id_temp = id_suma * 2 - 2
id_temp = id_suma * 2 + 4
for id_contador < 10 and id_contador > 0 ; id_contador = id_contador + 1 {
id_total = id_total + id_precio * 2
}
id_mensaje = "Fin del codigo"
"""