import threading
import time
from confia.monitor.facade import MonitorFacade
from confia.detection.facade import DetectorFacade

class Engine(object):
    """
    docstring
    """

    def __init__(self):
        # load json
        self.engine_frequency = 30
        self.engine_status = 'stopped'
        self.monitor_stream_time = 10
        self.process_id = 1

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
            print('Executando processo {} ...'.format(self.process_id))
            self.engine_status = 'running'
            
            monitor_status = self.monitor()
            if monitor_status == 'error':
                raise Exception()

            self.detector()
            time.sleep(5)

            self.interventor()
            time.sleep(5)
            
            print('Processo {} finalizado.\n'.format(self.process_id))
            self.process_id += 1
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
        status = monitor.run(interval=self.monitor_stream_time, process_id=self.process_id)
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