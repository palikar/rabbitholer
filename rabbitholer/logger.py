import sys
import os
import logging
import logging.handlers
import datetime


RESET = '\033[0m'
BOLD = '\033[1m'
GREEN = '\033[92m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RED = '\033[38;5;197m'

logging.VERBOSE = 5

def setup_logging(args):

    logging.getLogger().handlers = []

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('{1}%(asctime)s{2} [{0}%(levelname)s{2}] %(message)s'.format(CYAN, GREEN, RESET))
    sh_info = logging.StreamHandler(sys.stdout)
    sh_info.setFormatter(formatter)
    logger.addHandler(sh_info)
    

def debug(msg, *args):
    logging.debug(msg, *args)


def debug_cyan(msg, *args):
    logging.debug(CYAN + msg + RESET, *args)


def debug_red(msg, *args):
    logging.debug(RED + msg + RESET, *args)
