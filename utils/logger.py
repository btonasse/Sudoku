import logging

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

    # Formatters
    formatter = logging.Formatter('%(name)s:%(levelname)s: %(message)s')

    # Handler
    file_handler = logging.FileHandler(filepath, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(loglevel)
    logger.addHandler(file_handler)

    return logger

