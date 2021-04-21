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
            scraping.scrape_all_data()
            print("\tScraping finished.")
            
            # print('\tPersisting data')
            # twitter_stream.persist_data()
            # print('\tData persisted')
            
        except Exception:
            self.status = 'error'
            # TODO: executar rotinas de notificação e logging
        else:
            self.status = 'finished'
        finally:
            status = self.status
            self.status = 'stopped'
            return status
