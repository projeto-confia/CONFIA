from src.fcmanager.fact_check_manager import FactCheckManager
import logging
from src.config import Config as config


class FactCheckManagerFacade(object):
    """
    docstring
    """

    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        

    def run(self):
        try:
            self._logger.info('Running FactCheckManager...')
            FactCheckManager().run()
            self._logger.info('FactCheckManager finished.')
        except:
            raise
