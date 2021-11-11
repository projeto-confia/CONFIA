from src.scraping.scraping import ScrapingBoatosOrg
import logging
from src.config import Config as config


class ScrapingFacade(object):
    """
    docstring
    """

    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)


    def run(self):
        try:
            self._logger.info('Running Scraping...')
            ScrapingBoatosOrg().run()
            self._logger.info('Scraping finished.')
        except:
            raise
