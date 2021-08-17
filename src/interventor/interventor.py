import logging
from datetime import datetime
from src.config import Config as config
from src.interventor.dao import InterventorDAO
from src.apis.twitter import TwitterAPI
from src.utils.email import EmailAPI


# TODO: refactor to interface and concrete classes, one concrete for each FCA
class Interventor(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._twitter_api = TwitterAPI()
        self._email_api = EmailAPI()
        self._dao = InterventorDAO(config.INTERVENTOR.CURATOR)
        self._logger.info("Interventor initialized.")
        
        
    def run(self):
        self._process_news()
        self._process_curatorship()
        
        
    def _process_news(self):
        candidates = self._select_news_to_be_verified()
        if not candidates:
            return
        if config.INTERVENTOR.CURATOR:
            self._persist_news_to_curatorship(candidates)
            return
        self._persist_news(candidates)
                
                
    def _select_news_to_be_verified(self):
        """Select news according environments variables
        
        Returns:
            list: list of candidate news to be verified
        """
        pass
    
    
    def _persist_news_to_curatorship(self, news):
        similars, candidates_to_check = self._split_similar_news(news)
        self._persist_similars_to_curatorship(similars)
        self._persist_candidates_to_check_to_curatorship(candidates_to_check)
        
        
    def _split_similar_news(self, news):
        """Split news list in two: list of similars and list of not similars
        
        Identify records on news list that is similar to early published by FCA.
        Add FCA id news to those identified as similar.

        Args:
            news (list): list of news
        
        Returns:
            tuple: (list of similars, list of not similars)
        """
        pass
    
    
    def _persist_similars_to_curatorship(self, similars):
        """Persist list of similar news to be curated

        Args:
            similars (list): list of similar news
        """
        pass


    def _persist_candidates_to_check_to_curatorship(self, candidates_to_check):
        """Persist list of candidate news to be check to be curated

        Args:
            candidates (list): list of candidate news to be check
        """
        pass
    
    
    def _persist_news(self, news):
        similars, candidates_to_check = self._split_similar_news(news)
        self._process_similars(similars)
        self._process_candidates_to_check(candidates_to_check)
        
        
    def _process_similars(self, similars):
        self._persist_similar_news(similars)
        self._create_alert_job(similars, alert_type='similar')
    
        
    def _process_candidates_to_check(self, candidates_to_check):
        file_id = self._build_excel(candidates_to_check)
        self._create_send_job(file_id)
        self._create_alert_job(candidates_to_check, alert_type='detected')
    
    
    def _build_excel(self, candidates_to_check):
        """Build an excel file to be sent to FCA

        Args:
            candidates_to_check (list): list of candidate news to be check
            
        Returns:
            int: id of excel file that has been created
        """
        pass


    def _persist_similar_news(self, similars):
        """Persist similar news list into database

        Args:
            similars (list): list of similar news
        """
        pass
    
    
    def _create_alert_job(self, news, alert_type):
        """Add alerts in social media tasks into jobs queue

        Args:
            news (list): list of news
            alert_type (str): {'similar', 'detected'} type of alert.
        """
        
        assert alert_type in ('similar', 'detected')
        # TODO: build specific module in utils package to register jobs
        pass
    
    
    def _create_send_job(self, file_id):
        pass
    
    
    def _process_curatorship(self):
        while (curations := self._get_curations()):
            self._persist_news(curations)
    
    
    def _get_curations(self):
        """Get records already curated but not processed
        
        Returns:
            list: list of curations
        """
        pass
