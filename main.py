from tokenizador import MinimalTokenizer
from parser import Parser
from tipo_token import TokenType
from lexema import Lexema

def procesar_archivo(archivo_entrada: str):
    with open(archivo_entrada, 'r', encoding='utf-8') as file:
        lineas = file.readlines()

    for linea in lineas:
        print(f"Procesando línea: {linea.strip()}")
        # Usa el parser para analizar la línea
        parser = Parser(linea.strip())
        tokens = parser.parse()
        
        # Usa el MinimalTokenizer para encontrar tokens en el texto
        tokenizer = MinimalTokenizer(tokens)
        tokenizer.buscar_lexemas()

        # Imprime los tokens encontrados
        print("Tokens encontrados:")
        for lexema in tokenizer.tokenized_lex:
            print(lexema)

        print("Texto no tokenizado:")
        print(tokenizer.no_tokenized_lex)
        print("-" * 50)

if __name__ == "__main__":
    procesar_archivo("texto_corregido.txt")
