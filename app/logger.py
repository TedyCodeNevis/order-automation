import logging

from app.config import settings

logger_text = settings.LOG_LEVEL

def setup_logging():

    logger_level = getattr(
        logging,
        settings.LOG_LEVEL.upper(),
        logging.INFO
    )

    logging.basicConfig(
        level=logger_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )