from confia.fcmanager.fact_check_manager import FactCheckManager


class FactCheckManagerFacade(object):
    """
    docstring
    """

    def __init__(self):
        self.status = 'stopped'
        

    def run(self):
        try:
            print('Running FactCheckManager...')
            self.status = 'running'
            fact_check_manager = FactCheckManager()
            print('\tProcessing feed from agency...')
            fact_check_manager.process_agency_feed()
            print('\tPersisting data...')
            fact_check_manager.persist_data()
        except Exception:
            self.status = 'error'
            # TODO: executar rotinas de notificação e logging
        else:
            self.status = 'finished'
        finally:
            status = self.status
            self.status = 'stopped'
            return status