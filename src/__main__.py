from src.engine.engine import Engine
from src.config import Config as config
import logging, logging.handlers


def init_log(verbose=False, smtp_log=False):
    # Create a custom logger
    logger = logging.getLogger(config.LOGGING.NAME)
    logger.setLevel(logging.INFO)  # global level

    # file handler
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(config.LOGGING.AUTOMATA_FILE_PATH)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # smtp handler
    if smtp_log:
        smtp_handler = logging.handlers.SMTPHandler(mailhost=('smtp.gmail.com', 587),
                                                    fromaddr=config.EMAIL.ACCOUNT,
                                                    toaddrs=config.EMAIL.ACCOUNT,
                                                    subject='Log Alert',
                                                    credentials=(config.EMAIL.ACCOUNT, config.EMAIL.PASSWORD),
                                                    secure=())
        smtp_handler.setLevel(logging.WARNING)
        smtp_handler.setFormatter(file_format)
        logger.addHandler(smtp_handler)
    
    # stream handler
    if verbose:
        stream_format = logging.Formatter('%(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.NOTSET)
        stream_handler.setFormatter(stream_format)
        logger.addHandler(stream_handler)

    logger.info('Booting the system.')


if __name__ == '__main__':
    init_log(verbose=config.LOGGING.VERBOSE, smtp_log=config.LOGGING.SMTP_LOG)
    e = Engine()
    e.run()
