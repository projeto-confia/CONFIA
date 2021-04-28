import threading
import time
from confia.monitor.facade import MonitorFacade
from confia.detection.facade import DetectorFacade
from confia.scraping.facade import ScrapingFacade

class Engine(object):
    """
    docstring
    """

    def __init__(self):
        # TODO: implementar o load do json
        # load json
        self.engine_frequency = 21600  # 21.600 seconds == 6 hours
        self.engine_status = 'stopped'
        self.monitor_stream_time = 30
        self.scraping_initial_load = True

        # TODO: implementar
        # start logger


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
            print("Engine in process. Impossible start a new one.")
        elif self.engine_status == 'stopped':
            self.run_process()
        else:
            print("Engine unavailable.")
            # TODO: executar rotinas de notificação e logging


    def run_process(self):
        try:
            print('Running process ...')
            self.engine_status = 'running'
            
            monitor_status = self.monitor()
            if monitor_status == 'error':
                raise Exception()
            
            self.detector()

            self.interventor()
            time.sleep(5)
            
            scraping_status = self.scraping()
            if scraping_status == 'error':
                raise Exception()
            
            print('Process finished.\n')
        except:
            self.engine_status = 'paused'
            # TODO: executar rotinas de notificação e logging
        else:
            self.engine_status = 'stopped'

    
    def monitor(self):
        """
        docstring
        """
        monitor = MonitorFacade()
        status = monitor.run(interval=self.monitor_stream_time)
        print('Status returned by the monitor module: {}.'.format(status))
        return status


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
        print('Running Interventor...')
        
        
    def scraping(self):
        """
        docstring
        """
        scraping = ScrapingFacade()
        status = scraping.run(initial_load = self.scraping_initial_load)
        # TODO: refatorar - incluir a rotina de load inicial no init da engine
        #       tal rotina deverá verificar se existem dados populados no banco
        if self.scraping_initial_load:
            self.scraping_initial_load = False
        print('Status returned by the scraping module: {}.'.format(status))
        return status
