import logging


class FactCheckManager(object):
    
    def __init__(self):
        self._logger = logging.getLogger('automata')
        # other inicial actions
        self._logger.info('FactCheckManager initialized.')
    
    
    def process_agency_feed(self):
        self._logger.info('Processing feed from agency...')
        
    
    def persist_data(self):
        self._logger.info('Persisting data...')
