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
        # load json
        self.engine_frequency = 21600  # 21.600 seconds == 6 hours
        self.engine_status = 'stopped'
        self.monitor_stream_time = 30
        self.scraping_initial_load = True
        # self.process_id = 1

        # start logger


    def restart(self):
        """
        docstring
        """
        # load json


    def run(self):
        """
        docstring
        """
        threading.Timer(self.engine_frequency, self.run).start()
        if self.engine_status == 'running':
            print("Engine em processo. Não pode iniciar um novo.")
        elif self.engine_status == 'stopped':
            self.run_process()
        else:
            print("Engine unavailable")
            # TODO: executar rotinas de notificação e logging


    def run_process(self):
        try:
            # print('Executando processo {} ...'.format(self.process_id))
            print('Executando processo ...')
            self.engine_status = 'running'
            
            # monitor_status = self.monitor()
            # if monitor_status == 'error':
            #     raise Exception()
            
            # self.detector()
            # time.sleep(5)

            # self.interventor()
            # time.sleep(5)
            
            scraping_status = self.scraping()
            if scraping_status == 'error':
                raise Exception()
            
            # print('Processo {} finalizado.\n'.format(self.process_id))
            print('Processo finalizado.\n')
            # self.process_id += 1
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
        # status = monitor.run(interval=self.monitor_stream_time, process_id=self.process_id)
        status = monitor.run(interval=self.monitor_stream_time)
        print('Status retornado pelo monitor: {}.'.format(status))
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
        print('Executando Interventor...')
        
        
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
        print('Status retornado pelo scraping: {}.'.format(status))
        return status
