import time

class MonitorFacade(object):
    """
    docstring
    """
    def __init__(self):
        self.status = 'stopped'

    
    def run(self, interval, process_id):
        try:
            print('Executando Monitor...')
            self.status = 'running'
            time.sleep(interval)
            if process_id > 2:
                raise Exception()
        except Exception:
            self.status = 'error'
            # TODO: executar rotinas de notificação e logging
        else:
            self.status = 'finished'
        finally:
            status = self.status
            self.status = 'stopped'
            return status
