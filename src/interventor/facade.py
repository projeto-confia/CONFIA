from confia.interventor.interventor import Interventor


class InterventorFacade(object):
    """
    docstring
    """

    def __init__(self):
        self.status = 'stopped'


    def run(self):
        try:
            print('Running Interventor...')
            self.status = 'running'
            interventor = Interventor()
            interventor.select_news_to_be_checked()
            interventor.send_news_to_agency()
        except Exception:
            self.status = 'error'
            # TODO: executar rotinas de notificação e logging
        else:
            self.status = 'finished'
        finally:
            status = self.status
            self.status = 'stopped'
            return status
