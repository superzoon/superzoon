import logging

from os.path import isfile
from os import remove
LOG_FILE = "log.txt"
TAG = "xlan"

try:
    if isfile(LOG_FILE):
        remove(LOG_FILE)
except Exception as e:
    print('初始化log文件异常 {}'.format(e.args))

logger = logging.getLogger(TAG)

handler1 = logging.StreamHandler()
handler2 = logging.FileHandler(filename=LOG_FILE)

logger.setLevel(logging.DEBUG)
handler1.setLevel(logging.WARNING)
handler2.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
handler1.setFormatter(formatter)
handler2.setFormatter(formatter)

logger.addHandler(handler1)
logger.addHandler(handler2)

def debug(msg):
    logger.debug(msg)

def info(msg):
    logger.info(msg)

def info(msg):
    logger.info(msg)

def warning(msg):
    logger.warning(msg)

def error(msg):
    logger.error(msg)

def critical(msg):
    logger.critical(msg)
