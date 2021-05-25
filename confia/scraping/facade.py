from confia.scraping.scraping import Scraping


class ScrapingFacade(object):
    """
    docstring
    """

    def __init__(self):
        self.status = 'stopped'

    def run(self):
        try:
            print('Running Scraping...')
            self.status = 'running'
            scraping = Scraping()
            
            print("\tScraping initialized.")
            if not scraping.initial_load:
                print("\tUpdating data...")
                scraping.update_data()
            else:
                print("\tFetching data...")
                scraping.fetch_data()
            
            print('\tPersisting data...')
            # TODO: refatorar
            # chamar o método abaixo somente se há arquivo de dados
            scraping.persist_data()
            # print('\tData persisted.')
            
        except Exception:
            self.status = 'error'
            # TODO: executar rotinas de notificação e logging
        else:
            self.status = 'finished'
        finally:
            status = self.status
            self.status = 'stopped'
            return status
