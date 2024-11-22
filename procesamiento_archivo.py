import json
import os
from typing import Dict, TypeAlias, Optional

from lexema import Lexema
from tipo_token import TokenType

Dictlexemas: TypeAlias = Dict[str, Dict[str, Lexema]]
FILE = 'dictlexemas.json'


class FileManager:
    @staticmethod
    def leer_json(file_path: str):
        """Lee un archivo JSON y devuelve un diccionario."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, IOError) as e:
            print(f"Error al leer el archivo: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error al parsear el archivo JSON: {e}")
            return None

    @staticmethod
    def escribir_json(file_path: str, data):
        """Escribe el diccionario en un archivo JSON."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                serialized_data = {}
                for key, value in data.items():
                    serialized_value = {lex_key: lexema.to_dict() for lex_key, lexema in value.items()}
                    serialized_data[key] = serialized_value
                json.dump(serialized_data, file, ensure_ascii=False, indent=4)
        except (FileNotFoundError, IOError) as e:
            print(f"Error al leer el archivo: {e}")
        except json.JSONDecodeError as e:
            print(f"Error al parsear el archivo JSON: {e}")

    @classmethod
    def leer_dictlexemas(cls) -> Optional[Dictlexemas]:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, FILE)
        data = cls.leer_json(file_path)
        dictlexemas: Dictlexemas = {}
        for lexid, value in data.items():
            lexemas = {}
            for lexema_key, item in value.items():
                lexema = Lexema(
                    lexemas=item['lexemas'],
                    token=TokenType[item['token']],
                    peso=item['peso']
                )
                lexemas[lexema_key] = lexema
            dictlexemas[lexid] = lexemas

        return dictlexemas

    @classmethod
    def actualizar_dictlexemas(cls, lexema: Lexema):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, FILE)

        dictlexemas = cls.leer_dictlexemas()

        if lexema.raiz not in dictlexemas:
            dictlexemas[lexema.raiz] = {}

        if lexema.id not in dictlexemas[lexema.raiz]:
            dictlexemas[lexema.raiz][lexema.id] = lexema

        cls.escribir_json(file_path, dictlexemas)

    @classmethod
    def eliminar_lexemas(cls, key_to_delete):
        eliminado = False
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, FILE)
        data = cls.leer_dictlexemas()

        # Añade impresión de depuración
        print("Diccionario antes de eliminar:", data)
        print("Clave a eliminar:", key_to_delete)

        # Recorrer el diccionario padre
        for parent_key, child_dict in data.items():
            # Si la clave a eliminar está en el diccionario hijo
            if key_to_delete in child_dict:
                del child_dict[key_to_delete]
                print(f"Elemento '{key_to_delete}' eliminado correctamente del diccionario hijo '{parent_key}'.")
                eliminado = True
                # Si el diccionario hijo está vacío, eliminar también la clave del diccionario padre
                if not child_dict:
                    del data[parent_key]
                    print(f"El diccionario hijo '{parent_key}' está vacío y se ha eliminado del diccionario padre.")
                break
        else:
            print(f"La clave '{key_to_delete}' no existe en el diccionario.")
        if eliminado:
            # Guardar los cambios en el archivo JSON
            cls.escribir_json(file_path, data)
