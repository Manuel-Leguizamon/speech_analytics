from tokenizador import MinimalTokenizer
from parser import Parser
from tipo_token import TokenType
from lexema import Lexema
from tabulate import tabulate

def generar_resumen_sentimiento(tokenizer, categoria: str, puntaje: float):
    # Filtrar palabras positivas y negativas
    palabras_positivas = [
        lexema for lexema in tokenizer.tokenized_lex if lexema.token == TokenType.BUENO
    ]
    palabras_negativas = [
        lexema for lexema in tokenizer.tokenized_lex if lexema.token == TokenType.MALO or lexema.token == TokenType.PROHIBIDA
    ]
    
    # Encontrar la palabra más positiva y la más negativa
    palabra_mas_positiva = max(palabras_positivas, key=lambda lexema: lexema.peso, default=None)
    palabra_mas_negativa = max(palabras_negativas, key=lambda lexema: lexema.peso, default=None)

    # Crear las cadenas para mostrar las palabras positivas y negativas
    palabras_positivas_str = ", ".join([' '.join(lexema.lexemas) for lexema in palabras_positivas])
    palabras_negativas_str = ", ".join([' '.join(lexema.lexemas) for lexema in palabras_negativas])

    # Construir la tabla
    cuadro = [
        ["Categoría", categoria],
        ["Puntaje", puntaje],
        ["Palabras positivas", palabras_positivas_str if palabras_positivas else "Ninguna detectada"],
        ["Palabra más positiva", f"{' '.join(palabra_mas_positiva.lexemas)}, +{palabra_mas_positiva.peso}" if palabra_mas_positiva else "Ninguna detectada"],
        ["Palabras negativas", palabras_negativas_str if palabras_negativas else "Ninguna detectada"],
        ["Palabra más negativa", f"{' '.join(palabra_mas_negativa.lexemas)}, {palabra_mas_negativa.peso}" if palabra_mas_negativa else "Ninguna detectada"]
    ]

    # Imprimir la tabla con tabulate
    return tabulate(cuadro, headers=["Atributo", "Valor"], tablefmt="grid", stralign="center")



def generar_protocolo(tokenizer):
    # Definir las categorías a evaluar
    categorias = [
        ("Saludo", tokenizer.tiene_saludo, TokenType.SALUDO),
        ("Despedida", tokenizer.tiene_despedida, TokenType.DESPEDIDA),
        ("Identificación", tokenizer.tiene_identificacion, TokenType.IDENTIFICACION),
        ("Palabras Prohibidas", tokenizer.tiene_prohibidas, TokenType.PROHIBIDA)
    ]

    # Construir los datos para la tabla
    protocolo_datos = []
    for categoria, tiene_categoria, tipo_token in categorias:
        if tiene_categoria:  # Si la categoría está presente
            palabras_detectadas = [
                ' '.join(lexema.lexemas) for lexema in tokenizer.tokenized_lex
                if lexema.token == tipo_token and lexema.tag == 1  # Filtrar solo los lexemas con tag = 1
            ]
            if palabras_detectadas:
                protocolo_datos.append([categoria, "OK", ", ".join(palabras_detectadas)])
            else:
                protocolo_datos.append([categoria, "Ninguna detectada", ""])
        else:  # Si la categoría no está presente
            protocolo_datos.append([categoria, "Ninguna detectada", ""])

    # Crear la tabla con tabulate
    cuadro_protocolo = tabulate(
        protocolo_datos,
        headers=["Categoría", "Estado", "Palabras Detectadas"],
        tablefmt="grid",
        stralign="center"
    )

    return cuadro_protocolo


def procesar_archivo(archivo_entrada: str):
    # Leer todo el archivo como una sola cadena
    with open(archivo_entrada, 'r', encoding='utf-8') as file:
        texto_completo = file.read()

    print(f"Procesando archivo completo:\n{texto_completo}\n")
    
    # Usa el parser para analizar todo el archivo
    parser = Parser(texto_completo.strip())
    tokens = parser.parse()
    
    # Usa el MinimalTokenizer para encontrar tokens en el texto
    tokenizer = MinimalTokenizer(tokens)
    tokenizer.buscar_lexemas()

    # Obtener la evaluación
    resultado_evaluacion = tokenizer.evaluacion
    categoria, puntaje = resultado_evaluacion

    # Imprime los tokens encontrados
    print("Tokens encontrados:")
    for lexema in tokenizer.tokenized_lex:
        print(lexema)

    print("\nTexto no tokenizado:")
    print(tokenizer.no_tokenized_lex)
    
    print("\n\n")
    print("\n" + "*" * 50)

    #------------------------------------
    #       ANALISIS DE SENTIMIENTO      |
    #------------------------------------
    # Definimos el título
    titulo = [["Analisis De Sentimiento"]]
    # Generamos el cuadro para el título
    cuadro_titulo = tabulate(
        titulo, 
        tablefmt="grid", 
        stralign="center"
    )
    print(cuadro_titulo)
    print(generar_resumen_sentimiento(tokenizer, categoria,puntaje))
    print("\n" + "*" * 50 + "\n")


    #------------------------------------
    #       TABLA DE SIMBOLOS           |
    #------------------------------------
    titulo = [["Tabla De Simbolos"]]
    # Generamos el cuadro para el título
    cuadro_titulo = tabulate(
        titulo, 
        tablefmt="grid", 
        stralign="center"
    )
    print(cuadro_titulo)
     # Construimos la tabla de símbolos
    tabla_simbolos = [
        [lexema.raiz, lexema.peso, lexema.token.titulo]
        for lexema in tokenizer.tokenized_lex
    ]
    # Mostrar la tabla usando tabulate
    print(tabulate(tabla_simbolos, headers=["Lexema", "Ponderación", "Token"], tablefmt="grid"))
    print("\n" + "*" * 50 + "\n")


    #------------------------------------
    #      PROTOCOLO DE ATENCION         |
    #------------------------------------
    # Definimos el título
    titulo = [["Protocolo de Atencion"]]
    # Generamos el cuadro para el título
    cuadro_titulo = tabulate(
        titulo, 
        tablefmt="grid", 
        stralign="center"
    )
    print(cuadro_titulo)
    print(generar_protocolo(tokenizer))
    print("\n" + "*" * 50 + "\n")


if __name__ == "__main__":
    procesar_archivo("texto_corregido.txt")
