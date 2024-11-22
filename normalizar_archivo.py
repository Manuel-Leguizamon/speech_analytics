def unir_etiquetas_consecutivas(lineas: list[str]) -> list[str]:
    resultado = []
    linea_actual = ""

    for linea in lineas:
        etiqueta, texto = linea.split("-", 1)  # Divide en etiqueta y texto
        if not linea_actual:
            # Inicializa con la primera etiqueta y texto
            linea_actual = f"{etiqueta}-{texto}"
        else:
            etiqueta_actual, texto_actual = linea_actual.split("-", 1)
            if etiqueta == etiqueta_actual:
                # Une el texto si la etiqueta es la misma
                linea_actual = f"{etiqueta}-{texto_actual} {texto}"
            else:
                # Guarda la línea actual y comienza una nueva
                linea_actual = linea_actual.replace("\n", "") + "\n"
                resultado.append(linea_actual)
                linea_actual = f"{etiqueta}-{texto}"
            

    # Agregar la última línea procesada
    if linea_actual:
        resultado.append(linea_actual)

    return resultado
def guardar_resultado_en_archivo(resultado: list[str], archivo_salida: str):
    with open(archivo_salida, 'w', encoding='utf-8') as file:
        for linea in resultado:
            file.write(linea)

lineas = []
with open("texto.txt", 'r', encoding='utf-8') as file:
    lineas = file.readlines()
# Procesar las líneas
resultado = unir_etiquetas_consecutivas(lineas)

# Guardar el resultado en un archivo
archivo_salida = "texto_corregido.txt"
guardar_resultado_en_archivo(resultado, archivo_salida)
print(f"El resultado ha sido guardado en {archivo_salida}")