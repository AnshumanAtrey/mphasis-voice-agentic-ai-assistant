import logging
from config.settings import Settings

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(Settings.LOG_LEVEL)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(Settings.LOG_FORMAT)
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger
