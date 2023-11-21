import logging
import os
from datetime import date

"""
    Este módulo contiene la clase Logger para registrar los logs
"""


# Crear una clase Logger para registrar los logs
class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        # Crear el directorio "logs" si no existe
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Crear un handler para la consola
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.DEBUG)
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)

        # Crear un handler para el archivo de logs
        self.file_handler = logging.FileHandler("logs/" + str(date.today()) + ".log")
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, msg):
        self.logger.warning(msg)

    def critical(self, msg):
        self.logger.critical(msg)


# Creamos una instancia del logger para evitar crear múltiples instancias
logger = Logger("NexusPJLLM")
