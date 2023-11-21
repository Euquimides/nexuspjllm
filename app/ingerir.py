from llama_index import VectorStoreIndex, ServiceContext
from llama_index.vector_stores import ChromaVectorStore
from llama_index.storage.storage_context import StorageContext
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.schema import TextNode
from llama_index.indices.postprocessor import SentenceTransformerRerank
from llama_index.indices.query.schema import QueryBundle
from llama_index.retrievers import VectorIndexRetriever
from preprocesar import split
from consulta_nexus import consulta_nexus
from logs import logger
import keybert
import chromadb
import sys

"""
    Este script contiene las funciones necesarias para extraer, indexar y buscar nodos de jurisprudencia de NEXUS PJ.
    - extractor: extrae jurisprudencia de NEXUS PJ, la parte en chunks y lo transforma en nodos de tipo TextNode según el esquema de LlamaIndex
    - indexar: indexa los nodos.
    - buscar_nodos: realiza una búsqueda semántica de los nodos indexados conjuntamente con un reranker.
    - imprimir_nodos: imprime los resultados de la búsqueda.
    - guardar_nodos: guarda los resultados de la búsqueda en un archivo de texto.
"""

# Define el nombre del modelo
modelo = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Crea una instancia del modelo de embeddings
embedding_model = HuggingFaceEmbedding(model_name=modelo)


# Función para extraer nodos de jurisprudencia de NEXUS PJ
def extractor(consulta, embedding_model) -> list:
    try:
        # Preprocesa la consulta
        consulta = consulta.lower()
        consulta = consulta.replace("¿", "")
        consulta = consulta.replace("?", "")
        consulta = consulta.replace("¡", "")
        consulta = consulta.replace("!", "")
        consulta = consulta.replace("á", "a")
        consulta = consulta.replace("é", "e")
        consulta = consulta.replace("í", "i")
        consulta = consulta.replace("ó", "o")
        consulta = consulta.replace("ú", "u")
        consulta = consulta.replace("ü", "u")
        consulta = consulta.replace("ñ", "n")
        consulta = consulta.replace("  ", " ")
        consulta = consulta.replace(",", " ")
        consulta = consulta.replace(".", " ")
        consulta = consulta.strip()
               
        # Informa que la extracción de palabras clave ha iniciado
        logger.info("Extracción de palabras clave iniciada")

        # Asigna el modelo de embeddings a la instancia de KeyBERT
        kw_modelo = keybert.KeyBERT(model=embedding_model)

        # Genera las palabras clave con base en la consulta
        palabras_clave = kw_modelo.extract_keywords(
            consulta, keyphrase_ngram_range=(1, 1), stop_words=None
        )

        # Extrae las palabras clave de la lista de palabras clave generadas
        palabras_clave = [
            palabra_clave[0] for palabra_clave in palabras_clave if palabra_clave[1]
        ]

        # Ordena las palabras clave según el orden de aparición en la consulta
        palabras_clave = ordenar_palabras_clave(consulta, palabras_clave)

        # Informa que la extracción de palabras clave ha finalizado
        logger.info("Extracción de palabras clave finalizada")

        # Muestra en logs las palabras clave extraídas
        logger.info("Palabras clave extraídas: " + str(palabras_clave))

        # Concatena las palabras clave en una cadena de texto separado por un espacio en blanco y un AND (&)
        palabras_clave = " & ".join(palabras_clave)

        # Mostramos en logs la consulta a NEXUS PJ
        logger.info("Consulta a NEXUS PJ: " + palabras_clave)

        # Realiza la consulta a la API de NEXUS PJ
        response = consulta_nexus(palabras_clave)

        # Creamos una lista vacía para almacenar todos los nodos
        nodes = []

        for hit in response["hits"]:
            # Extrae el valor de "content"
            content = hit["content"]
            # Llamamos a la función "split" para partir el contenido en chunks
            chunks = split(content)
            # Agregamos los chunks como un objeto TextNode a una lista a la que le asociamos el "idDocument", el "despacho", el "expediente", el "tipoInformacion" y el "date"
            chunks = [
                TextNode(
                    text=chunk,
                    metadata={
                        "ID_Sentencia": hit["idDocument"],
                        "Despacho": hit["despacho"],
                        "Expediente": hit["expediente"],
                        "Tipo de Información": hit["tipoInformacion"],
                        "Fecha": hit["date"],
                    },
                )
                for chunk in chunks
            ]
            # Agregamos los TextNodes a la lista "nodes"
            nodes.extend(chunks)
            # Agregamos información de depuración para ver el progreso
            logger.info("Procesando nodos...")
    except:
        # Agregamos información de error
        logger.error("Error: " + str(sys.exc_info()[0]))
        # Imprimimos el error
        print(sys.exc_info()[0])
        # Terminamos el programa dado el error
        sys.exit(1)
    else:
        # Agregamos información de depuración para ver el progreso
        logger.info("Nodos procesados")
        # Retornamos la lista de nodos
        return nodes


# Función para indexar los nodos
def indexar(nodes, embedding_model):
    # Informamos que el índice está siendo creado
    logger.info("Creando índice...")
    # Creamos un cliente y una nueva colección
    # TODO: Cambiar a un cliente persistente
    client = chromadb.EphemeralClient()
    client_collection = client.create_collection("sentencias")

    # Creamos el vector store
    vector_store = ChromaVectorStore(chroma_collection=client_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = ServiceContext.from_defaults(
        embed_model=embedding_model, llm=None
    )

    # Creamos el índice
    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        service_context=service_context,
        llm=None,
        show_progress=True,
    )
    # Informamos que el índice ha sido creado
    logger.info("Índice creado")
    # Retornamos el índice
    return index


# Función para buscar nodos
def buscar_nodos(
    consulta, index, vector_top_k=int, reranker_top_n=None, with_reranker_sbert=False
):
    # Informamos que la búsqueda ha iniciado
    logger.info("Iniciando búsqueda...")
    query_bundle = QueryBundle(consulta)
    # Se configura el retriever
    retriever = VectorIndexRetriever(index=index, similarity_top_k=vector_top_k)
    retrieved_nodes = retriever.retrieve(query_bundle)
    # Se configura el reranker
    if with_reranker_sbert:
        reranker = SentenceTransformerRerank(
            model="nreimers/mmarco-mMiniLMv2-L12-H384-v1", top_n=reranker_top_n
        )
        retrieved_nodes = reranker.postprocess_nodes(retrieved_nodes, query_bundle)
    # Informamos que la búsqueda ha finalizado
    logger.info("Búsqueda finalizada")
    # Retornamos los nodos
    return retrieved_nodes


# Función para imprimir los nodos
def imprimir_nodos(retrieved_nodes):
    # Imprimimos los nodos
    for node in retrieved_nodes:
        print("--------------------------------------------------")
        print("Chunk:", node.text)
        print("ID del Chunk:", node.id_)
        print("ID de la Sentencia:", node.metadata["ID_Sentencia"])
        print("Despacho:", node.metadata["Despacho"])
        print("Expediente:", node.metadata["Expediente"])
        print("Tipo de información:", node.metadata["Tipo de Información"])
        print("Fecha:", node.metadata["Fecha"])
        print("--------------------------------------------------")
        print("")


# Función para guardar los nodos en un archivo de texto
def guardar_nodos(retrieved_nodes):
    # Guarda la estructura del print en un archivo de texto
    with open("chunks.txt", "w") as f:
        for node in retrieved_nodes:
            f.write("--------------------------------------------------" + "\n")
            f.write("Chunk: " + node.text + "\n")
            f.write("ID del Chunk: " + node.id_ + "\n")
            f.write("ID de la Sentencia: " + node.metadata["ID_Sentencia"] + "\n")
            f.write("Despacho: " + node.metadata["Despacho"] + "\n")
            f.write("Expediente: " + node.metadata["Expediente"] + "\n")
            f.write(
                "Tipo de información: " + node.metadata["Tipo de Información"] + "\n"
            )
            f.write("Fecha: " + node.metadata["Fecha"] + "\n")
            f.write("--------------------------------------------------" + "\n")
            f.write("\n")


def ordenar_palabras_clave(consulta, palabras_clave):
    # Split the string into individual words
    palabras = consulta.split()

    # Create a dictionary to map each word to its index in the original string
    indices_palabras = {palabra: i for i, palabra in enumerate(palabras)}

    # Sort the keywords by their indices in the original string
    palabras_clave_ordenadas = sorted(palabras_clave, key=lambda x: indices_palabras[x])

    return palabras_clave_ordenadas
