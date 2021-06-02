from src.interventor.interventor import Interventor
import logging
from src.config import Config as config


class InterventorFacade(object):
    """
    docstring
    """

    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)


    def run(self):
        try:
            self._logger.info('Running Interventor...')
            interventor = Interventor()
            interventor.select_news_to_be_checked()
            interventor.send_news_to_agency()
            self._logger.info('Interventor finished.')
        except:
            raise
