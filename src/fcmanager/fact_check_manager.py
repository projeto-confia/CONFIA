import logging
from src.config import Config as config
from src.fcmanager.dao import FactCheckManagerDAO


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
            return
        
        fakenews_ids = self._dao.get_fakenews_ids_from_excel()

        # if has no records, stop process
        if not fakenews_ids:
            return
        
        # update filtered records into database
            # if some id record doesn't exist in the database table, register occurrence in the log
        
        # move excel file to ./data/acf/processed folder
        
        
        self._logger.info('Processing feed from agency...')
        
        
    
    def persist_data(self):
        self._logger.info('Persisting data...')
