import time
from confia.monitor.stream import TwitterStream

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
            twitter_stream = TwitterStream()
            print("\tTwitter Streaming initialized.")
            print("\tStreaming for {} seconds...".format(interval))
            twitter_stream.collect_data(interval=interval)
            print("\tStreaming finished.")
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

