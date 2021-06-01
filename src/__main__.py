from src.engine.engine import Engine
import logging


def init_log(verbose=False):
    # Create a custom logger
    logger = logging.getLogger('automata')
    logger.setLevel(logging.INFO)  # global level

    # file handler
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('logs/automata.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # TODO: acrescentar handler smtp
    
    if verbose:
        stream_format = logging.Formatter('%(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(stream_format)
        logger.addHandler(stream_handler)

    logger.info('Booting the system.')


if __name__ == '__main__':
    init_log()
    e = Engine()
    e.run()