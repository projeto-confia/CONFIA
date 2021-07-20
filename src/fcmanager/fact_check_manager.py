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
    
    
    def process_agency_feed(self):
        
        if not self._dao.has_excel_file():
            self._logger.info('No excel file to process.')
            return
        
        self._logger.info('Processing feed from agency...')
        checked_fakenews = self._dao.get_checked_fakenews_from_excel()

        if checked_fakenews:
            self._logger.info('Updating data...')
            self._dao.update_checked_news_in_db(checked_fakenews)
        else:
            self._logger.info('No labeled fake news.')
            
        self._logger.info('Storing excel file...')
        self._dao.store_excel_file()
