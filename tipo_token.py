from enum import Enum


class TokenType(Enum):
    BUENO = "BUENO"
    MALO = "MALO"
    NEUTRAL = "NEUTRAL"
    SALUDO = "SALUDO"
    DESPEDIDA = "DESPEDIDA"
    IDENTIFICACION = "IDENTIFICACION"
    PROHIBIDA = "PROHIBIDA"

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
        elif self == TokenType.IDENTIFICACION:
            return "IDENTIFICACION"
        elif self == TokenType.PROHIBIDA:
            return "PROHIBIDA"
        else:
            return "NEUTRAL"

    def pesos_por_defecto(self):
        if self == TokenType.BUENO:
            return 2
        elif self == TokenType.MALO:
            return -2
        elif self == TokenType.SALUDO:
            return 1
        elif self == TokenType.DESPEDIDA:
            return 1
        elif self == TokenType.IDENTIFICACION:
            return 1
        elif self == TokenType.PROHIBIDA:
            return -4
        else:
            return 0
