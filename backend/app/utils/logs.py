import logging
import os
import traceback
from datetime import date
import colorlog

class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )

        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        os.makedirs("logs", exist_ok=True)

        self.console_handler = colorlog.StreamHandler()
        self.console_handler.setLevel(logging.DEBUG)
        self.console_handler.setFormatter(console_formatter)
        self.logger.addHandler(self.console_handler)

        self.file_handler = logging.FileHandler(f"logs/{date.today()}.log")
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(file_formatter)
        self.logger.addHandler(self.file_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        exc_info = traceback.format_exc()
        self.logger.error(f"{message}\n{exc_info}")

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, msg):
        self.logger.warning(msg)

    def critical(self, msg):
        self.logger.critical(msg)

logger = Logger("NexusPJLLM")