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
            
            self.monitor()
            # if monitor_status == 'error':
            #     raise Exception()
            
            self.fact_check_manager()
            # if fact_check_manager_status == 'error':
            #     raise Exception()
            
            self.detector()

            self.interventor()
            # if interventor_status == 'error':
            #     raise Exception()
            
            self.scraping()
            # if scraping_status == 'error':
            #     raise Exception()
            
            self.engine_status = 'stopped'
            self._logger.info('Process finished.')
        except:
            self.engine_status = 'error'
            self._logger.critical('Engine in critical status.', exc_info=True)
            raise

    
    def monitor(self):
        """
        docstring
        """
        monitor = MonitorFacade()
        monitor.run(interval=self.monitor_stream_time)
        # print('Status returned by the monitor module: {}.'.format(status))
        # return monitor.status


    def detector(self):
        """
        docstring
        """
        detector = DetectorFacade()
        detector.run()
        # status = detector.run(interval=self.monitor_stream_time, process_id=self.process_id)
        # print('Status retornado pelo detector: {}.'.format(status))
        # return status


    def interventor(self):
        """
        docstring
        """
        interventor = InterventorFacade()
        status = interventor.run()
        print('Status returned by the interventor module: {}.'.format(status))
        return status
        
        
    def scraping(self):
        """
        docstring
        """
        scraping = ScrapingFacade()
        status = scraping.run()
        print('Status returned by the scraping module: {}.'.format(status))
        return status


    def fact_check_manager(self):
        """
        docstring
        """
        fact_check_manager = FactCheckManagerFacade()
        status = fact_check_manager.run()
        print('Status returned by the fcmanager module: {}.'.format(status))
        return status
        