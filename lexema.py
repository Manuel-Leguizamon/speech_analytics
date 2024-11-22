from typing import List
from tipo_token import TokenType


class Lexema:
    def __init__(self, lexemas: List[str], token: TokenType, peso: int):
        self.id: str = '_'.join(lexemas)
        self.lexemas: List[str] = lexemas
        self.token: TokenType = token
        if token == TokenType.NEUTRAL:
            self.peso = 0
            self.pesoO = 0
        else:
            self.peso = peso
            self.pesoO = peso
        self.length: int = len(lexemas)

    def __str__(self):
        return f"Lexema({' '.join(self.lexemas)}): {self.token.titulo}"

    @property
    def raiz(self):
        return self.lexemas[0]

    def to_dict(self):
        return {
            'id': self.id,
            'lexemas': self.lexemas,
            'token': self.token.value,  # Use .value to get the enum value
            'peso': self.peso,
            'length': self.length
        }
