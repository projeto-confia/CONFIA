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
            print("\tInterventor initialized.")
            print("\tSelecting news to be checked...")
            interventor.select_news_to_check()
            print("\tSending selected news to agency...")
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