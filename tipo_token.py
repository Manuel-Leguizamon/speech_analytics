from enum import Enum


class TokenType(Enum):
    BUENO = "BUENO"
    MALO = "MALO"
    NEUTRAL = "NEUTRAL"
    SALUDO = "SALUDO"
    DESPEDIDA = "DESPEDIDA"

    @property
    def titulo(self):
        if self == TokenType.BUENO:
            return "BUENO"
        elif self == TokenType.MALO:
            return "MALO"
        elif self == TokenType.SALUDO:
            return "SALUDO"
        elif self == TokenType.DESPEDIDA:
            return "DESPEDIDA"
        else:
            return "NEUTRAL"

    def pesos_por_defecto(self):
        if self == TokenType.BUENO:
            return 2
        elif self == TokenType.MALO:
            return 4
        elif self == TokenType.SALUDO:
            return 3
        elif self == TokenType.DESPEDIDA:
            return 3
        else:
            return 0
