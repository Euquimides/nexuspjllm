import os
import sys
import uuid

import chromadb
import keybert
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.indices.postprocessor import SentenceTransformerRerank
from llama_index.indices.query.schema import QueryBundle
from llama_index.llms import OpenAI
from llama_index.prompts import PromptTemplate
from llama_index.response_synthesizers import ResponseMode, get_response_synthesizer
from llama_index.retrievers import VectorIndexRetriever
from llama_index.schema import TextNode
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import ChromaVectorStore

from .consulta_nexus import consulta_nexus
from .logs import logger
from .preprocesar import split

"""
    Este script contiene las funciones necesarias para extraer, indexar y buscar nodos de jurisprudencia de NEXUS PJ.
    - extractor: extrae jurisprudencia de NEXUS PJ, la parte en chunks y lo transforma en nodos de tipo TextNode según el esquema de LlamaIndex.
    - indexar: indexa los nodos.
    - buscar_nodos: realiza una búsqueda semántica de los nodos indexados conjuntamente con un reranker.
    - imprimir_nodos: imprime los resultados de la búsqueda.
    - guardar_nodos: guarda los resultados de la búsqueda en un archivo de texto.
    - sintetizador_respuesta: sintetiza una respuesta con base en la consulta y los nodos extraídos.
"""

# Define el nombre del modelo
modelo = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Crea una instancia del modelo de embeddings
embedding_model = HuggingFaceEmbedding(model_name=modelo)

# Crea una instancia del modelo de lenguaje
llm = OpenAI(model="gpt-3.5-turbo", api_key="NULL", api_base="http://localhost:1234/v1")

# Define el Servicio de Contexto
servicio_de_contexto = ServiceContext.from_defaults(
    embed_model=embedding_model, llm=llm
)

# Define un nuevo prompt en español
qa_prompt_tmpl_es_str = """\
    La información de contexto se encuentra a continuación.
    ---------------------
    {context_str}
    ---------------------
    Dada la información de contexto y sin conocimiento previo, responde a la consulta en el lenguaje español. \
    Sea conciso en su respuesta.
    Consulta: {query_str}
    Respuesta: \
    """

# Crear un Prompt Template con el prompt en español
qa_prompt_tmpl_es = PromptTemplate(qa_prompt_tmpl_es_str)


# Función para extraer nodos de jurisprudencia de NEXUS PJ
def extractor(consulta, embedding_model, use_keybert=False) -> list:
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

        # Extrae las palabras clave de la consulta si use_keybert es True
        if use_keybert == True:
            # Informa que la extracción de palabras clave ha iniciado
            logger.info("Extracción de palabras clave iniciada")

            # Asigna el modelo de embeddings a la instancia de KeyBERT
            kw_modelo = keybert.KeyBERT(model=embedding_model)

            # Genera las palabras clave con base en la consulta
            palabras_clave = kw_modelo.extract_keywords(
                consulta, keyphrase_ngram_range=(1, 2), top_n=2
            )

            # Genera las palabras clave con base en la consulta
            palabras_clave = keybert.extract_keywords(
                consulta, keyphrase_ngram_range=(1, 2), top_n=2
            )
            # Extrae las palabras clave de la lista de palabras clave generadas
            palabras_clave = [
                palabra_clave[0] for palabra_clave in palabras_clave if palabra_clave[1]
            ]

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
        else:
            # Realiza la consulta directa a la API de NEXUS PJ
            response = consulta_nexus(consulta)

            # Mostramos en logs la consulta a NEXUS PJ
            logger.info("Consulta a NEXUS PJ: " + consulta)

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
def indexar(nodes):
    # Informamos que el índice está siendo creado
    logger.info("Creando índice...")
    # Creamos un cliente y una nueva colección
    client = chromadb.PersistentClient(path="./app/chroma_db")
    client_collection = client.get_or_create_collection("sentencias")
    # Creamos el vector store
    vector_store = ChromaVectorStore(chroma_collection=client_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = servicio_de_contexto

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
    # Imprimimos los nodos como logs
    for node in retrieved_nodes:
        logger.info("--------------------------------------------------")
        logger.info("Chunk: " + node.text)
        logger.info("ID del Chunk: " + node.id_)
        logger.info("ID de la Sentencia: " + node.metadata["ID_Sentencia"])
        logger.info("Despacho: " + node.metadata["Despacho"])
        logger.info("Expediente: " + node.metadata["Expediente"])
        logger.info("Tipo de información: " + node.metadata["Tipo de Información"])
        logger.info("Fecha: " + node.metadata["Fecha"])
        logger.info("--------------------------------------------------")
        logger.info("")


# Función para guardar los nodos en un archivo de texto
def guardar_nodos(retrieved_nodes):
    # Crea un nombre para el archivo de texto con un identificador único
    nombre_archivo = "chunks/chunks" + str(uuid.uuid4()) + ".txt"
    # Si no existe el directorio "chunks", lo crea
    if not os.path.exists("chunks"):
        os.makedirs("chunks")
    # Guarda la estructura del print en el archivo de texto
    with open(nombre_archivo, "w") as f:
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


# Función para sintetizar una respuesta usando un modelo de lenguaje
def sintetizador_respuesta(consulta, retrieved_nodes):
    # Se configura el sintetizador de respuestas
    response_synthesizer = get_response_synthesizer(
        response_mode=ResponseMode.COMPACT,
        verbose=True,
        service_context=servicio_de_contexto,
    )
    # Se actualiza el prompt
    response_synthesizer.update_prompts({"text_qa_template": qa_prompt_tmpl_es})
    # Se configura la respuesta
    respuesta = response_synthesizer.synthesize(consulta, retrieved_nodes)
    # Retornamos la respuesta
    return respuesta


# Obtener el índice
def get_index():
    # Creamos o obtenemos un cliente y una nueva colección
    client = chromadb.PersistentClient(path="./app/chroma_db")
    client_collection = client.get_or_create_collection("sentencias")
    # Creamos el vector store
    vector_store = ChromaVectorStore(chroma_collection=client_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = servicio_de_contexto
    # Cargamos el índice
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        service_context=service_context,
        storage_context=storage_context,
    )
    # Retornamos el índice
    return index