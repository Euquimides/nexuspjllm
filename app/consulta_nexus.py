from logs import logger
import requests
import json
import sys

"""
    Este módulo contiene la función para consultar la API de NEXUS PJ
"""


# Función para consulta de NEXUS PJ
def consulta_nexus(palabras_clave):
    try:
        # Define el URL de la API de NEXUS PJ
        url = "https://nexuspj.poder-judicial.go.cr/api/search"

        # Define los parámetros de la consulta
        params = {
            "q": palabras_clave,
            "nq": "",
            "advanced": False,
            "facets": [],
            "size": 10,
            "page": 1,
            "sort": {"field": "contenidosInteresOrden", "order": "desc"},
            "exp": "",
        }

        # Define los headers de la consulta
        headers = {"Content-Type": "application/json"}

        # Realiza la consulta a la API de NEXUS PJ
        response = requests.post(url, headers=headers, data=json.dumps(params))

        # Convierte la respuesta de la API de NEXUS PJ en un diccionario
        response = response.json()
    except:
        # Informa del error
        logger.error(
            "Error al realizar la consulta a NEXUS PJ. Error: " + str(sys.exc_info()[0])
        )
        # Define la respuesta como None
        response = None
    finally:
        # Retorna la respuesta
        return response
