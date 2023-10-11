import logging


# Wrapper of logging module to share a single instance between python files
class Log:
    def __init__(self, name):
        logging.basicConfig(filename=f'{name}.log', filemode='w', format='%(levelname)s - %(message)s')

    def error(self, msg):
        logging.error(msg)

    def warning(self, msg):
        logging.warning(msg)
