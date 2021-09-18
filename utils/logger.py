import logging
import logging.handlers

def create_logger(name: str, filepath: str, loglevel: int = logging.WARNING) -> logging.Logger:
    '''
    Set up a logger and return it. Logs are written to a file.
        Args:
            name: name of the logger
            filepath: where the file handler saves the logs
            loglevel: level to which set the logger
    '''
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)

    # Formatter
    formatter = logging.Formatter('%(name)s:%(levelname)s: %(message)s')

    # Handlers
    file_handler = logging.handlers.RotatingFileHandler(filepath, mode='w', encoding='utf-8', maxBytes=1000000, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(loglevel)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(max(loglevel, logging.WARNING))
    logger.addHandler(console_handler)

    return logger

