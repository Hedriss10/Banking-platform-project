# src/utils/log.py

from src.models.models import Log
from src.db.database import db
from datetime import datetime
import logging



# setup logger para console e arquivo
def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        file_handler = logging.FileHandler("src.log")
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# salva o log no banco de dados
def log_to_db(logger_name: str, level: str, message: str):
    try:
        log_entry = Log(
            timestamp=datetime.utcnow(),  # <-- força o valor
            logger_name=logger_name,
            level=level,
            message=message
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        logger = setup_logger("DBLogger")
        logger.error(f"Erro ao salvar log no banco: {e}")

logger = setup_logger("AppLogger")

def logdb(level: str, message: str):
    """
    Salva log no console/arquivo e também no banco de dados.
    """
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message)
    log_to_db("AppLogger", level.upper(), message)


# logdb("warning", "Not found") example
# logdb("info", "Users list is empty")
# logdb("error", "Not found")   