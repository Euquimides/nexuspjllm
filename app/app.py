from ingerir import *
from logs import logger

# Informamos del inicio de la app
logger.info("NexusPJLLM app iniciada")
try:
    # Solicitamos la consulta al usuario
    consulta = input("Ingrese su consulta: ")
    # Extraemos los nodos de jurisprudencia de NEXUS PJ
    nodes = extractor(consulta, embedding_model)
    # Indexamos los nodos
    index = indexar(nodes, embedding_model)
    # Buscamos los nodos
    retrieved_nodes = buscar_nodos(
        consulta, index, vector_top_k=10, reranker_top_n=3, with_reranker_sbert=True
    )
    # Imprimimos los nodos
    imprimir_nodos(retrieved_nodes)
    # Guardamos los nodos en un archivo de texto
    guardar_nodos(retrieved_nodes)
    pass
except Exception as e:
    # Informamos del error
    logger.error("Error: " + str(e))
finally:
    # Informamos del fin de la app
    logger.info("NexusPJLLM app finalizada")
