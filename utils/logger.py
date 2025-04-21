import logging
import sys
from config import LOG_LEVEL, LOG_FORMAT


def setup_logger(name: str) -> logging.Logger:
    """ Set up and configure a logger instance """

    logger = logging.getLogger(name) # logger creation

    # set level from config
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # create console handler if no handlers exist
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # create formatter
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)

        logger.addHandler(handler) # add handler to logger

    return logger