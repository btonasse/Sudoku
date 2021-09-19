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

    # Formatter
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    file_formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')

    # Handlers
    file_handler = logging.FileHandler(filepath, mode='w', encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(loglevel)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(max(loglevel, logging.WARNING))
    logger.addHandler(console_handler)

    return logger

