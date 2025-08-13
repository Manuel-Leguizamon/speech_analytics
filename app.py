import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, request, redirect, url_for, flash
from tabulate import tabulate

# Importa tus módulos existentes (asegurate de que estén en el PYTHONPATH)
from tokenizador import MinimalTokenizer
from parser import Parser
from tipo_token import TokenType
from lexema import Lexema
import unicodedata

def _normalize_text(s: str) -> str:
    if not s:
        return ""
    # unificar saltos, quitar NBSP, normalizar unicode
    s = s.replace("\r\n", "\n").replace("\r", "\n").replace("\u00A0", " ")
    # NFKC: normaliza comillas raras, porcentajes, etc.
    s = unicodedata.normalize("NFKC", s)
    return s.strip()

app = Flask(__name__)

@app.after_request
def add_no_cache_headers(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")

def _tok_name(t):
    # Soporta Enum, string o cualquier objeto con .name
    return getattr(t, "name", str(t))

def _is_token(lx, token_member):
    return _tok_name(lx.token) == _tok_name(token_member)


def generar_resumen_sentimiento(tokenizer, categoria: str, puntaje: float):
    palabras_positivas = [lx for lx in tokenizer.tokenized_lex if _is_token(lx, TokenType.BUENO)]
    palabras_negativas = [lx for lx in tokenizer.tokenized_lex if _is_token(lx, TokenType.MALO) or _is_token(lx, TokenType.PROHIBIDA)]

    palabra_mas_positiva = max(palabras_positivas, key=lambda lx: lx.peso, default=None)
    palabra_mas_negativa = max(palabras_negativas, key=lambda lx: lx.peso, default=None)

    palabras_positivas_str = ", ".join([' '.join(lx.lexemas) for lx in palabras_positivas]) if palabras_positivas else "Ninguna detectada"
    palabras_negativas_str = ", ".join([' '.join(lx.lexemas) for lx in palabras_negativas]) if palabras_negativas else "Ninguna detectada"

    cuadro = [
        ["Categoría", categoria],
        ["Puntaje", puntaje],
        ["Palabras positivas", palabras_positivas_str],
        ["Palabra más positiva", f"{' '.join(palabra_mas_positiva.lexemas)}, +{palabra_mas_positiva.peso}" if palabra_mas_positiva else "Ninguna detectada"],
        ["Palabras negativas", palabras_negativas_str],
        ["Palabra más negativa", f"{' '.join(palabra_mas_negativa.lexemas)}, {palabra_mas_negativa.peso}" if palabra_mas_negativa else "Ninguna detectada"],
    ]
    return tabulate(cuadro, headers=["Atributo", "Valor"], tablefmt="html", stralign="center")

def generar_protocolo(tokenizer):
    categorias = [
        ("Saludo", tokenizer.tiene_saludo, TokenType.SALUDO),
        ("Despedida", tokenizer.tiene_despedida, TokenType.DESPEDIDA),
        ("Identificación", tokenizer.tiene_identificacion, TokenType.IDENTIFICACION),
        ("Palabras Prohibidas", tokenizer.tiene_prohibidas, TokenType.PROHIBIDA),
    ]

    protocolo_datos = []
    for categoria, tiene_categoria, tipo_token in categorias:
        if tiene_categoria:
            palabras_detectadas = [
                ' '.join(lx.lexemas) for lx in tokenizer.tokenized_lex if _is_token(lx, tipo_token) and getattr(lx, "tag", 0) == 1
            ]
            if palabras_detectadas:
                protocolo_datos.append([categoria, "OK", ", ".join(palabras_detectadas)])
            else:
                protocolo_datos.append([categoria, "Ninguna detectada", ""])
        else:
            protocolo_datos.append([categoria, "Ninguna detectada", ""])

    return tabulate(
        protocolo_datos,
        headers=["Categoría", "Estado", "Palabras Detectadas"],
        tablefmt="html",
        stralign="center",
    )

def analizar_texto(texto_completo: str):
    parser = Parser(texto_completo.strip())
    tokens = parser.parse()

    tokenizer = MinimalTokenizer(tokens)
    tokenizer.buscar_lexemas()

    categoria, puntaje = tokenizer.evaluacion

    # Título “Análisis de Sentimiento”
    titulo_sent_html = tabulate([["Analisis De Sentimiento"]], tablefmt="html", stralign="center")
    resumen_sent_html = generar_resumen_sentimiento(tokenizer, categoria, puntaje)

    # Tabla de símbolos
    titulo_tabla_simbolos_html = tabulate([["Tabla De Simbolos"]], tablefmt="html", stralign="center")
    tabla_simbolos = [
        [' '.join(lx.lexemas), lx.pesoO, lx.token.titulo] for lx in tokenizer.tokenized_lex
    ]
    tabla_simbolos_html = tabulate(tabla_simbolos, headers=["Lexema", "Ponderación", "Token"], tablefmt="html", stralign="center")

    # Protocolo de Atención
    titulo_protocolo_html = tabulate([["Protocolo de Atencion"]], tablefmt="html", stralign="center")
    protocolo_html = generar_protocolo(tokenizer)

    # Extras para mostrar
    tokens_encontrados = tokenizer.tokenized_lex
    no_tokenizado = tokenizer.no_tokenized_lex

    return {
        "titulo_sent_html": titulo_sent_html,
        "resumen_sent_html": resumen_sent_html,
        "titulo_tabla_simbolos_html": titulo_tabla_simbolos_html,
        "tabla_simbolos_html": tabla_simbolos_html,
        "titulo_protocolo_html": titulo_protocolo_html,
        "protocolo_html": protocolo_html,
        "tokens_encontrados": tokens_encontrados,
        "no_tokenizado": no_tokenizado,
        "categoria": categoria,
        "puntaje": puntaje,
    }

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    texto_inicial = ""

    if request.method == "POST":
        # Prioridad: archivo -> textarea
        file = request.files.get("archivo")
        texto = request.form.get("texto", "").strip()

        if file and file.filename:
            data = file.read()  # bytes
            texto_inicial = None
            for enc in ("utf-8", "cp1252", "latin-1"):
                try:
                    texto_inicial = data.decode(enc)
                    break
                except UnicodeDecodeError:
                    pass
            if texto_inicial is None:
                texto_inicial = data.decode("utf-8", errors="replace")
        else:
            flash("Cargá un archivo .txt o pegá texto para analizar.", "warning")
            return redirect(url_for("index"))

        try:
            texto_inicial = _normalize_text(texto_inicial)
            resultado = analizar_texto(texto_inicial)
        except Exception as e:
            # Muestra error amigable (ej: si falta algún módulo)
            flash(f"Ocurrió un error durante el análisis: {e}", "error")

    return render_template("index.html", resultado=resultado, texto_inicial=texto_inicial)

if __name__ == "__main__":
    # Permite FLASK_DEBUG=1 en dev
    app.run(host="127.0.0.1", port=5000, debug=True)
