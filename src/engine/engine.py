import threading
import logging
from src.monitor.facade import MonitorFacade
from src.detection.facade import DetectorFacade
from src.scraping.facade import ScrapingFacade
from src.fcmanager.facade import FactCheckManagerFacade
from src.interventor.facade import InterventorFacade
from src.config import Config as config


class Engine(object):
    """
    docstring
    """

    def __init__(self):
        
        # logging
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self.engine_status = config.STATUS.STOPPED
        self._logger.info('System ready.')


    def restart(self):
        """
        docstring
        """
        # TODO: implementar
        # load config


    def run(self):
        """
        docstring
        """
        threading.Timer(config.ENGINE.FREQUENCY, self.run).start()
        if self.engine_status == config.STATUS.RUNNING :
            self._logger.warning("Engine in processing. Impossible start a new one.")
        elif self.engine_status == config.STATUS.STOPPED:
            self.run_process()
        else:
            self._logger.error("Engine unavailable.")


    def run_process(self):
        try:
            self._logger.info('Running process...')
            self.engine_status = config.STATUS.RUNNING
            
            if config.ENGINE.SCRAPING_ACTIVATED:
                ScrapingFacade().run()
            if config.ENGINE.FACT_CHECK_MANAGER_ACTIVATED:
                FactCheckManagerFacade().run()
            if config.ENGINE.MONITOR_ACTIVATED:
                MonitorFacade().run()
            if config.ENGINE.DETECTOR_ACTIVATED:
                DetectorFacade().run()
            if config.ENGINE.INTERVENTOR_ACTIVATED:
                InterventorFacade().run()
            
            self.engine_status = config.STATUS.STOPPED
            self._logger.info('Process finished.')
        except:
            self.engine_status = config.STATUS.ERROR
            self._logger.critical('Engine in critical status.', exc_info=True)
            raise
