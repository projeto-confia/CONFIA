import logging
from datetime import datetime
from src.config import Config as config
from src.interventor.dao import InterventorDAO
from src.apis.twitter import TwitterAPI
from src.utils.email import EmailAPI
from src.utils.text_preprocessing import TextPreprocessing


# TODO: refactor to interface and concrete classes, one concrete for each FCA
class Interventor(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._twitter_api = TwitterAPI()
        self._email_api = EmailAPI()
        self._dao = InterventorDAO(config.INTERVENTOR.CURATOR)
        self._text_preprocessor = TextPreprocessing()
        self._all_fca_news = self._get_all_agency_news()
        self._logger.info("Interventor initialized.")
        
        
    def run(self):
        # self._process_news()
        self._process_curatorship()
        
        
    def _get_all_agency_news(self):
        all_fca_news = self._dao.get_all_agency_news()
        for i, (_, publication_title, _) in enumerate(all_fca_news):
            all_fca_news[i] += (self._text_preprocessor.text_cleaning(publication_title),)
        return all_fca_news
        
        
    def _process_news(self):
        self._logger.info('Selecting news to be verified...')
        candidates = self._dao.select_news_to_be_verified(window_size=config.INTERVENTOR.WINDOW_SIZE,
                                                          prob_classif_threshold=config.INTERVENTOR.PROB_CLASSIF_THRESHOLD,
                                                          num_records=config.INTERVENTOR.NUM_NEWS_TO_SELECT)
        if not candidates:
            self._logger.info('No news to be verified.')
            return
        if config.INTERVENTOR.CURATOR:
            self._persist_news_to_curatorship(candidates)
            return
        self._persist_news(candidates)
                
                
    def _persist_news_to_curatorship(self, news):
        self._logger.info('Persisting news to curatorship...')
        similars, candidates_to_check = self._split_similar_news(news)
        candidates_to_check = [c + (None,) for c in candidates_to_check]
        self._dao.persist_to_curatorship(similars + candidates_to_check)
        
        
    def _split_similar_news(self, news):
        """Split news list in two: list of similars and list of not similars
        
        Identify records on news list that is similar to early published by FCA.
        Add FCA id news to those identified as similar.

        Args:
            news (list): list of news
        
        Returns:
            tuple: (list of similars, list of not similars)
        """
        
        similars, not_similars = list(), list()
        for i, (_, text_news) in enumerate(news):
            text_news_cleaned = self._text_preprocessor.text_cleaning(text_news)
            for id_news_checked, _, _, publication_title_cleaned in self._all_fca_news:
                is_similar, _ = self._text_preprocessor.check_duplications(text_news_cleaned, publication_title_cleaned)
                if is_similar:
                    similars.append(news[i] + (id_news_checked,))
                    break
            else:
                not_similars.append(news[i])
        return (similars, not_similars)
    
    
    def _persist_news(self, news):
        """Process and persist selected classified fakenews
        
        News must be a list of tuples like (id_news, text_news)

        Args:
            news (list): list of tuples like (id_news, text_news)
        """
        
        self._logger.info('Processing news...')
        similars, candidates_to_check = self._split_similar_news(news)
        self._process_similars(similars)
        self._process_candidates_to_check(candidates_to_check)
        
        
    def _process_similars(self, similars):
        self._logger.info('Processing similar news...')
        self._dao.persist_similar_news(similars)
        # TODO: implement create alert job function
        # self._create_alert_job(similars, alert_type='similar')
    
        
    def _process_candidates_to_check(self, candidates_to_check):
        self._logger.info('Processing news to be checked...')
        if config.INTERVENTOR.CURATOR:
            curated = [c for c in candidates_to_check if c[3] != None]
            candidates_to_check = [c for c in candidates_to_check if c[3] == None]
            if curated:
                self._process_labeled_curatorship(curated)
            if not candidates_to_check:
                return
        candidates_id = [c[0] for c in candidates_to_check]
        id_trusted_agency,_,_,_ = self._dao.get_data_from_agency('Boatos.org')
        self._dao.persist_candidates_to_check(candidates_id, id_trusted_agency)
        # TODO: implement functions
        # file_id = self._build_excel(candidates_to_check)
        # self._create_send_job(file_id)
        # self._create_alert_job(candidates_to_check, alert_type='detected')
        
        
    def _process_labeled_curatorship(self, curated):
        print([c[0] for c in curated])
    
    
    def _build_excel(self, candidates_to_check):
        """Build an excel file to be sent to FCA

        Args:
            candidates_to_check (list): list of candidate news to be check
            
        Returns:
            int: id of excel file that has been created
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
        while (curations := self._dao.get_curations()):
            self._logger.info('Processing curated news...')
            curations_id = [curation[5] for curation in curations]
            similars = [curation[:3] for curation in curations if curation[4]]
            candidates_to_check = [curation[:4] for curation in curations if not curation[4]]
            if similars:
                self._process_similars(similars)
            if candidates_to_check:
                self._process_candidates_to_check(candidates_to_check)
            self._dao.close_curations(tuple(curations_id))
        else:
            self._logger.info('No more curations to be process.')
