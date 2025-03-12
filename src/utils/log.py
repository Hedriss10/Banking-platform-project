import logging
from src.db.pg import PgAdmin

def setup_logger(name: str):
    """
    Sets up a logger object with a given name.
    The logger will write both
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

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

def log_to_db(logger_name: str, level: str, message: str):
    db = PgAdmin()
    query = f"""
        INSERT INTO logs (timestamp, logger_name, level, message)
        VALUES (NOW(), '{logger_name}', '{level}', '{message}');
    """
    db.execute_query(query=query)
    db.commit()

# config loggs
logger = setup_logger("AppLogger")

def logs_and_save_db(level, message):
    # logg save in db
    log_function = getattr(logger, level.lower())
    log_function(message)
    log_to_db("AppLogger", level.upper(), message)


# logs_and_save_db("warning", "Not found") example