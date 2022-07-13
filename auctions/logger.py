import logging
import os


class LoggerAuctions:
    # Add logger
    f_handler = logging.FileHandler('general.log')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.addHandler(LoggerAuctions.f_handler)
        self.logger.setLevel('DEBUG')
