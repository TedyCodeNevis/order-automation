import logging

from config import LOG_LEVEL

logger_text = LOG_LEVEL

def setup_logging():

    logger_level = getattr(
        logging,
        LOG_LEVEL.upper(),
        logging.INFO
    )

    logging.basicConfig(
        level=logger_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )