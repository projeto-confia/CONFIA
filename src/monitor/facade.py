import logging
from src.config import Config as config
from src.monitor.monitor import Monitor


class MonitorFacade(object):
    """
    docstring
    """

    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)

    def run(self):
        try:
            self._logger.info('Running Monitor...')
            Monitor().run()
            self._logger.info('Monitor finished.')
        except:
            raise
