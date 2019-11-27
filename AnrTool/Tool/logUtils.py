import logging
from Tool import GLOBAL_VALUES

if GLOBAL_VALUES.debug:
    logger = logging.getLogger("xlan")

    handler1 = logging.StreamHandler()
    handler2 = logging.FileHandler(filename="log.txt")

    logger.setLevel(logging.DEBUG)
    handler1.setLevel(logging.WARNING)
    handler2.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    handler1.setFormatter(formatter)
    handler2.setFormatter(formatter)

    logger.addHandler(handler1)
    logger.addHandler(handler2)

def debug(msg):
    if GLOBAL_VALUES.debug:
        logger.debug(msg)

def info(msg):
    if GLOBAL_VALUES.debug:
        logger.info(msg)

def info(msg):
    if GLOBAL_VALUES.debug:
        logger.info(msg)

def warning(msg):
    if GLOBAL_VALUES.debug:
        logger.warning(msg)

def error(msg):
    if GLOBAL_VALUES.debug:
        logger.error(msg)

def critical(msg):
    if GLOBAL_VALUES.debug:
        logger.critical(msg)
