import logging


class DbLogger:
    def __init__(self, msg: str):
        self.msg = msg



def setup_logger(name: str):
    """
    Sets up a logger with the specified name. The logger outputs to both
    the console and a file named 'src.log'. Console logs are set to INFO level,
    while file logs are set to DEBUG level. The logs are formatted to include
    the timestamp, logger name, log level, and message.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler('src.log')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger