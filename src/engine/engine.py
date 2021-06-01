import threading
import logging
from src.monitor.facade import MonitorFacade
from src.detection.facade import DetectorFacade
from src.scraping.facade import ScrapingFacade
from src.fcmanager.facade import FactCheckManagerFacade
from src.interventor.facade import InterventorFacade


class Engine(object):
    """
    docstring
    """

    def __init__(self):
        
        # logging
        self._logger = logging.getLogger('automata')
        
        # TODO: implementar o load do json
        # load json
        self.engine_frequency = 21600    # 21.600 seconds == 6 hours
        self.engine_status = 'stopped'
        self.monitor_stream_time = 1200  # 1.200 seconds == 20 minutes
        self._logger.info('System ready.')


    def restart(self):
        """
        docstring
        """
        # TODO: implementar
        # load json


    def run(self):
        """
        docstring
        """
        threading.Timer(self.engine_frequency, self.run).start()
        if self.engine_status == 'running':
            self._logger.warning("Engine in processing. Impossible start a new one.")
        elif self.engine_status == 'stopped':
            self.run_process()
        else:
            self._logger.error("Engine unavailable.")
            # TODO: executar rotinas de notificação e logging


    def run_process(self):
        try:
            self._logger.info('Running process...')
            self.engine_status = 'running'
            
            MonitorFacade().run(interval=self.monitor_stream_time)
            FactCheckManagerFacade().run()
            DetectorFacade().run()
            InterventorFacade().run()
            ScrapingFacade().run()
            
            self.engine_status = 'stopped'
            self._logger.info('Process finished.')
        except:
            self.engine_status = 'error'
            self._logger.critical('Engine in critical status.', exc_info=True)
            raise
