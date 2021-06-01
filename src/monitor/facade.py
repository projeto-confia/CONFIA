from src.monitor.stream import TwitterStream
import logging


class MonitorFacade(object):
    """
    docstring
    """

    def __init__(self):
        self._logger = logging.getLogger('automata')

    def run(self, interval):
        try:
            self._logger.info('Running Monitor...')
            twitter_stream = TwitterStream(interval=interval)
            twitter_stream.collect_data()
            twitter_stream.persist_data()
            self._logger.info('Monitor finished.')
        except:
            raise
