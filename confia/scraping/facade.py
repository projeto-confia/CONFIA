from confia.scraping.scraping import Scraping


class ScrapingFacade(object):
    """
    docstring
    """

    def __init__(self):
        self.status = 'stopped'

    def run(self, initial_load):
        try:
            print('Running Scraping...')
            self.status = 'running'
            scraping = Scraping()
            
            print("\tScraping initialized.")
            if not initial_load:
                print("\tUpdating data...")
                scraping.update_data()
            else:
                print("\tFetching data...")
                scraping.fetch_data()
            print("\tScraping finished.")
            
            print('\tPersisting data...')
            # TODO: refatorar
            # chamar o método abaixo somente se há arquivo de dados
            # talvez os métodos fetch_data() e update_data() possam retornar essa informação
            scraping.persist_data(initial_load)
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
