import logging
from src.config import Config as config
from src.fcmanager.dao import FactCheckManagerDAO


# TODO: refactor to interface and concrete classes, one concrete for each ACF
class FactCheckManager(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._dao = FactCheckManagerDAO()
        self._logger.info('FactCheckManager initialized.')
        
        
    def run(self):
        self.process_agency_feed()
        self.persist_data()
    
    
    def process_agency_feed(self):
        
        # If has not excel file, stop process
        if not self._dao.has_excel_file():
            self._logger.info('No excel file to process.')
            return
        
        self._logger.info('Processing feed from agency...')
        fakenews_ids = self._dao.get_fakenews_ids_from_excel()

        # if has no records, stop process
        if not fakenews_ids:
            self._logger.info('No labeled fake news.')
            return
        
        # update filtered records into database
        self._logger.info('Updating data...')
        self._dao.update_checked_news_in_db(fakenews_ids)
        
    
    def persist_data(self):
        self._logger.info('Persisting data...')
