import logging
from logging.handlers import RotatingFileHandler

def logger_setup(logger, log_file_name):
    #create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    # create file handler which logs even debug messages
    fh = RotatingFileHandler(log_file_name, maxBytes=10000000, backupCount=100, encoding='utf-8')
    fh.doRollover()
    fh.setLevel(logging.DEBUG)

    # add formatter to fh
    fh.setFormatter(formatter)

    # add fh to logger
    logger.addHandler(fh)