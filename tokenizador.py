from collections import deque
from typing import List, Optional, Tuple

from procesamiento_archivo import FileManager, Dictlexemas
from lexema import Lexema
from tipo_token import TokenType


class MinimalTokenizer:
    def __init__(self, linea: List[str]):
        # Eliminar la etiqueta y el guion, y luego dividir cada elemento en palabras
        self.linea = []
        for cadena in linea:
            # Eliminar los primeros dos caracteres (etiqueta y guion)
            cadena_sin_etiqueta = cadena[2:]
            # Dividir la cadena en palabras y agregar cada palabra como un elemento en la lista
            self.linea.extend(cadena_sin_etiqueta.split())  # `split()` divide la cadena por espacios
        
        self.dictlexemas: Dictlexemas = FileManager.leer_dictlexemas()
        self.tokenized_lex: List[Lexema] = []
        self.no_tokenized_lex: List[str] = []
        self.token_types_found: set[TokenType] = set()

    @property
    def tiene_saludo(self) -> bool:
        return TokenType.SALUDO in self.token_types_found

    @property
    def tiene_despedida(self) -> bool:
        return TokenType.DESPEDIDA in self.token_types_found
    @property
    def tiene_identificacion(self) -> bool:
        return TokenType.IDENTIFICACION in self.token_types_found
    @property
    def tiene_prohibidas(self) -> bool:
        return TokenType.PROHIBIDA in self.token_types_found

    @property
    def evaluacion(self) -> Tuple[str, float]:
        bueno_sum, malo_sum, saludo_peso, despedida_peso, identif_peso, prohi_peso = self.__categorizar_sumar_pesos()
        bueno_normalizado, malo_normalizado, saludo_normalizado, despedida_normalizado, identif_normalizado, prohi_normalizado = (
            self.__normalizar_pesos(bueno_sum, malo_sum, saludo_peso, despedida_peso,identif_peso,prohi_peso)
        )
        puntaje = self.__evaluacion_final(
            bueno_normalizado, malo_normalizado, saludo_normalizado, despedida_normalizado, identif_normalizado, prohi_normalizado
        )
        return self.__map_categoria_to_puntaje(puntaje), puntaje

    def __categorizar_sumar_pesos(self) -> Tuple[int, int, int, int,int,int]:
        bueno_sum = 0
        malo_sum = 0
        saludo_peso = 0
        despedida_peso = 0
        identif_peso = 0
        prohi_peso = 0
        for lexema in self.tokenized_lex:
            if lexema.token == TokenType.BUENO:
                bueno_sum += lexema.peso * lexema.token.pesos_por_defecto()
            elif lexema.token == TokenType.MALO:
                malo_sum += lexema.peso * lexema.token.pesos_por_defecto()
            elif lexema.token == TokenType.SALUDO:
                saludo_peso += lexema.peso * lexema.token.pesos_por_defecto()
            elif lexema.token == TokenType.DESPEDIDA:
                despedida_peso += lexema.peso * lexema.token.pesos_por_defecto()
            elif lexema.token == TokenType.IDENTIFICACION:
                identif_peso += lexema.peso * lexema.token.pesos_por_defecto()
            elif lexema.token == TokenType.PROHIBIDA:
                prohi_peso += lexema.peso * lexema.token.pesos_por_defecto()
        return bueno_sum, malo_sum, saludo_peso, despedida_peso, identif_peso, prohi_peso

    @staticmethod
    def __normalizar_pesos(bueno_sum: int, malo_sum: int, saludo_peso: int, despedida_peso: int, identif_peso: int, prohi_peso: int) -> (
            Tuple
    )[float, float, float, float, float, float]:
        total = bueno_sum + malo_sum + saludo_peso + despedida_peso + identif_peso + prohi_peso
        if total == 0:
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0  # Avoid division by zero
        bueno_normalizado = bueno_sum / total
        malo_normalizado = malo_sum / total
        saludo_peso_normalizado = saludo_peso / total
        despedida_peso_normalizado = despedida_peso / total
        identif_normalizado = identif_peso / total
        prohi_normalizado = prohi_peso / total
        return bueno_normalizado, malo_normalizado, saludo_peso_normalizado, despedida_peso_normalizado, identif_normalizado, prohi_normalizado

    def __evaluacion_final(self, bueno_normalizado: float, malo_normalizado: float, saludo_normalizado: float,
                           despedida_normalizado: float, identif_normalizado: float, prohi_normalizado: float) -> float:
        if not self.tiene_saludo:
            # saludo_normalizado += 0.03  # Si tiene saludo
            # else:
            saludo_normalizado -= 0.3 * TokenType.SALUDO.pesos_por_defecto()

        if not self.tiene_despedida:
            # despedida_normalizado += 0.03  # Si tiene despedida
            # else:
            despedida_normalizado -= 0.3 * TokenType.SALUDO.pesos_por_defecto()

        return bueno_normalizado - malo_normalizado + saludo_normalizado + despedida_normalizado + identif_normalizado - prohi_normalizado

    @staticmethod
    def __map_categoria_to_puntaje(puntaje: float) -> str:
        if puntaje <= -0.5:
            return '1 MUY_MALA'
        elif -0.5 < puntaje <= -0.1:
            return '2 MALA'
        elif -0.1 < puntaje <= 0.1:
            return '3 NEUTRA'
        elif 0.1 < puntaje <= 0.5:
            return '4 BUENA'
        else:
            return '5 MUY_BUENA'

    def buscar_lexemas(self):
        linea_to_map = deque(self.linea)
        self.tokenized_lex = []
        self.no_tokenized_lex = []
        processed_lexemas = {}
        while linea_to_map:
            palabra = linea_to_map[0]
            if palabra in self.dictlexemas:
                lexemas = list(self.dictlexemas[palabra].values())
                lexema = self.__buscar_mejor_match(list(linea_to_map), lexemas)
                if lexema:
                    if lexema.id in processed_lexemas:
                        # Incrementa el peso del lexema ya procesado
                        processed_lexemas[lexema.id].peso += lexema.pesoO
                    else:
                        # Añade el nuevo lexema a tokenized_lex y marca como procesado
                        self.tokenized_lex.append(lexema)
                        self.token_types_found.add(lexema.token)
                        processed_lexemas[lexema.id] = lexema
                    # Remueve los elementos procesados de linea_to_map
                    for _ in range(lexema.length):
                        linea_to_map.popleft()
                else:
                    self.no_tokenized_lex.append(linea_to_map.popleft())
            else:
                self.no_tokenized_lex.append(linea_to_map.popleft())

    def __buscar_mejor_match(self, linea_to_map: List[str], lexemas: List[Lexema]) -> Optional[Lexema]:
        linea = '_'.join(linea_to_map)
        search_results: List[Lexema] = [
            lexema for lexema in lexemas if self.__esta_en_orden(lexema.id, linea)
        ]

        return max(search_results, key=lambda lexema: lexema.length, default=None)

    @staticmethod
    def __esta_en_orden(str1: str, str2: str) -> bool:
        return str2.startswith(str1)