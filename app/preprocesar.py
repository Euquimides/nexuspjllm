from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

"""
    Funciones para partir texto en chunks y preprocesarlos
"""


# Función para partir texto en chunks
def split(content):
    # Crea una instancia del splitter
    splitter = RecursiveCharacterTextSplitter(
        separators=[", ", ". ", " (", ") ", ": ", " - ", "\n"],
        chunk_size=1024,
        chunk_overlap=15,
        length_function=len,
        is_separator_regex=False,
    )
    # Partimos el contenido en chunks
    chunks = splitter.split_text(content)
    # Unimos los saltos de línea de cada chunk en una sola línea
    chunks = ["".join(chunk.splitlines()) for chunk in chunks]
    # Removemos los puntos y comas al inicio de cada chunk
    chunks = [re.sub(r"^[,.]", "", chunk) for chunk in chunks]
    # Eliminamos los correos electrónicos y lo sustituimos por la palabra "[Correo]"
    chunks = [re.sub(r"[\w\.-]+@[\w\.-]+", "[Correo]", chunk) for chunk in chunks]
    # Removemos bullet-points
    chunks = [re.sub(r"•", "", chunk) for chunk in chunks]
    # Chequear si el caracter es imprimible, si no, lo removemos
    chunks = [
        "".join([char for char in chunk if char.isprintable()]) for chunk in chunks
    ]
    # Si el chunk es menor a 100 caracteres, lo removemos
    chunks = [chunk for chunk in chunks if len(chunk) > 100]
    # Removemos los espacio en blanco al inicio y al final de cada chunk
    chunks = [chunk.strip() for chunk in chunks]
    # Retornamos los chunks
    return chunks
