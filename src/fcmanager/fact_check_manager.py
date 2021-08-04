import logging
from src.config import Config as config
from src.fcmanager.dao import FactCheckManagerDAO
from src.apis.twitter import TwitterAPI


# TODO: refactor to interface and concrete classes, one concrete for each ACF
class FactCheckManager(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._dao = FactCheckManagerDAO()
        self._twitter_api = TwitterAPI()
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
            if config.FCMANAGER.SOCIAL_MEDIA_ALERT_ACTIVATE:
                for v in checked_fakenews.values():
                    text_news, link = v.values()
                    self._post_alert(text_news, 'Boatos.org', link)
        else:
            self._logger.info('No labeled fake news.')
            
        self._logger.info('Storing excel file...')
        self._dao.store_excel_file()


    def _post_alert(self, text_news, checker, url=None):
        self._logger.info('Posting alert on social media...')
        header = 'ALERTA: a seguinte notícia foi confirmada como fakenews pela agência {}'.format(checker)

        # TODO: define strategy to fit tweet text according twitter limit rules            
        header = ''
            
        text_tweet = header + '\n\n' + text_news + '\n\n' + '{}'.format(url if url else '')
        self._twitter_api.tweet(text_tweet)
