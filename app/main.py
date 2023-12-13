import os

from utils.ingerir import *
from utils.logs import logger

"""
Este módulo contiene el código principal de la aplicación. Incluye la lógica para la interacción con el usuario.
"""

# Informamos del inicio de la app
logger.info("NexusPJLLM app iniciada")
# Inicializamos el index como None
index = None


def imprimir_opciones():
    # Imprimimos las siguientes opciones
    print("Seleccione una opción:")
    print("1. Consulta a NexusPJ y extracción de jurisprudencia relacionada")
    print("2. Generación inteligente de respuestas con base a jurisprudencia extraída")
    print("3. Top 3 de jurisprudencia más relevante según consulta a base de datos")
    print("4. Salir")
    print("")


try:
    # Damos un mensaje de bienvenida
    print("Bienvenido a NexusPJLLM")
    print("")
    # Imprimimos las opciones
    imprimir_opciones()
    # Solicitamos la opción al usuario
    opcion = input("Ingrese una opción: ")
    print("")
    # Mientras la opción no sea 3, se ejecuta el programa
    while opcion != "4":
        # Si la opción es 1, se ejecuta la consulta inteligente
        if opcion == "1":
            while True:
                # Solicitamos la consulta al usuario
                consulta = input(
                    "Ingrese su consulta sobre un tema jurídico particular (por ejemplo, derecho laboral): "
                )
                # Extraemos los nodos de jurisprudencia de NEXUS PJ
                nodes = extractor(consulta, embedding_model)
                # Indexamos los nodos
                index = indexar(nodes)
                # Buscamos los nodos y extraemos los top 20
                retrieved_nodes = buscar_nodos(
                    consulta,
                    index,
                    vector_top_k=20,
                    reranker_top_n=3,
                    with_reranker_sbert=False,
                )
                # Imprimimos los nodos
                imprimir_nodos(retrieved_nodes)
                # Guardamos los nodos en un archivo de texto
                guardar_nodos(retrieved_nodes)
                # Informamos que se terminó la indexación y guardado de nodos
                logger.info(
                    "Indexación y guardado de nodos finalizado. Base de datos vectorial en ./app/chroma_db"
                )
                print("")
                # Preguntamos si el usuario desea realizar otra consulta
                opcion = input("¿Desea realizar otra consulta? (S/N): ").lower()
                print("")
                # Si la respuesta es "n", se sale del ciclo
                if opcion == "n":
                    break
                # Si la respuesta es "s", se continúa con el ciclo
                elif opcion == "s":
                    continue
                # Si la respuesta no es "s" o "n", se solicita de nuevo
                else:
                    # Solicitamos la opción al usuario
                    opcion = input("Opción inválida. Responda sí o no (S/N): ").lower()
                    print("")
            # Volvemos a imprimir las opciones
            imprimir_opciones()
            # Solicitamos la opción al usuario
            opcion = input("Ingrese una opción: ")
        # Si la opción es 2, se ejecuta el chatbot
        elif opcion == "2":
            # Revisamos que exista una base de datos de chroma
            if not os.path.exists("./app/chroma_db"):
                # Informamos al usuario que debe ingerir la jurisprudencia
                print(
                    "Debe ingerir la jurisprudencia primero. Seleccione la opción 1 para iniciar con su primera consulta o 3 para salir."
                )
                print("")
                # Imprimimos las opciones
                imprimir_opciones()
                # Solicitamos la opción al usuario
                opcion = input("Ingrese una opción: ")
            else:
                while True:
                    # Solicitamos la consulta al usuario
                    consulta = input("Ingrese su consulta: ")
                    # Obtenemos el índice
                    index = get_index()
                    # Buscamos los nodos
                    retrieved_nodes = buscar_nodos(
                        consulta,
                        index,
                        vector_top_k=20,
                        reranker_top_n=3,
                        with_reranker_sbert=True,
                    )
                    # Imprimimos los nodos
                    imprimir_nodos(retrieved_nodes)
                    # Informamos del inicio de la síntesis de respuesta
                    logger.info(
                        "Iniciando síntesis de respuesta. Esto tomará unos minutos..."
                    )
                    # Sintetizar respuesta
                    respuesta = sintetizador_respuesta(consulta, retrieved_nodes)
                    # Imprimir la consulta de forma amigable
                    print("--------------------------------------------------")
                    print("Su consulta fue:")
                    print(consulta)
                    print("--------------------------------------------------")
                    # Imprimir respuesta de forma amigable
                    print("Respuesta generada:")
                    print(respuesta)
                    print("--------------------------------------------------")
                    print("")
                    # Informamos del fin de la síntesis de respuesta
                    logger.info("Síntesis de respuesta finalizada")
                    print("")
                    # Preguntamos si el usuario desea realizar otra consulta
                    opcion = input("¿Desea realizar otra consulta? (S/N): ").lower()
                    print("")
                    # Si la respuesta es "n", se sale del ciclo
                    if opcion == "n":
                        break
                    # Si la respuesta es "s", se continúa con el ciclo
                    elif opcion == "s":
                        continue
            # Volvemos a imprimir las opciones
            imprimir_opciones()
            # Solicitamos la opción al usuario
            opcion = input("Ingrese una opción: ")
        elif opcion == "3":
            # Revisamos que exista una base de datos de chroma
            if not os.path.exists("./app/chroma_db"):
                # Informamos al usuario que debe ingerir la jurisprudencia
                print(
                    "Debe ingerir la jurisprudencia primero. Seleccione la opción 1 para iniciar con su primera consulta o 3 para salir."
                )
                print("")
                # Imprimimos las opciones
                imprimir_opciones()
                # Solicitamos la opción al usuario
                opcion = input("Ingrese una opción: ")
            else:
                while True:
                    # Solicitamos la consulta al usuario
                    consulta = input("Ingrese su consulta: ")
                    # Obtenemos el índice
                    index = get_index()
                    # Buscamos los nodos
                    retrieved_nodes = buscar_nodos(
                        consulta,
                        index,
                        vector_top_k=20,
                        reranker_top_n=3,
                        with_reranker_sbert=True,
                    )
                    # Imprimir la consulta de forma amigable
                    print("--------------------------------------------------")
                    print("Su consulta fue:")
                    print(consulta)
                    print("--------------------------------------------------")
                    # Imprimir respuesta de forma amigable
                    print("Top 3 de jurisprudencia más relevante:")
                    # Imprimimos los nodos
                    imprimir_nodos(retrieved_nodes)
                    print("--------------------------------------------------")
                    print("")
                    # Guardamos los nodos en un archivo de texto
                    guardar_nodos(retrieved_nodes)
                    # Preguntamos si el usuario desea realizar otra consulta
                    opcion = input("¿Desea realizar otra consulta? (S/N): ").lower()
                    print("")
                    # Si la respuesta es "n", se sale del ciclo
                    if opcion == "n":
                        break
                    # Si la respuesta es "s", se continúa con el ciclo
                    elif opcion == "s":
                        continue
            # Volvemos a imprimir las opciones
            imprimir_opciones()
            # Solicitamos la opción al usuario
            opcion = input("Ingrese una opción: ")
        # Si la opción no es 1, 2 o 3, se solicita de nuevo
        elif opcion != "1" and opcion != "2" and opcion != "3" and opcion != "4":
            # Solicitamos la opción al usuario
            opcion = input("Ingrese una opción válida: ")
            print("")

    pass
except Exception as e:
    # Informamos del error
    logger.error("Error: " + str(e))
finally:
    # Informamos del fin de la app
    logger.info("NexusPJLLM app finalizada")
