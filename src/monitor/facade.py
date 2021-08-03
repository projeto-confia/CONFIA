from src.monitor.stream import TwitterMediaCollector, TwitterStream
import logging
from src.config import Config as config


class MonitorFacade(object):
    """
    docstring
    """

    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)

    def run(self):
        try:
            self._logger.info('Running Monitor...')
            TwitterMediaCollector().run()
            twitter_stream = TwitterStream()
            twitter_stream.collect_data()
            twitter_stream.persist_data()
            self._logger.info('Monitor finished.')
        except:
            raise
