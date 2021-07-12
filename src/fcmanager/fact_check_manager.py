import logging
from src.config import Config as config


class FactCheckManager(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        # other inicial actions
        self._logger.info('FactCheckManager initialized.')
        
        
    def run(self):
        self.process_agency_feed()
        self.persist_data()
    
    
    def process_agency_feed(self):
        self._logger.info('Processing feed from agency...')
        
    
    def persist_data(self):
        self._logger.info('Persisting data...')
