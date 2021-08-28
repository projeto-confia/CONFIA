import re
import abc
import logging
# TODO: transferir authconfig para config.py
import src.monitor.authconfig as cfg
from src.config import Config as config
from src.monitor.dao import MonitorDAO
from unicodedata import normalize
from src.apis.twitter import TwitterAPI


class CollectorInterface(metaclass=abc.ABCMeta):
    """Interface to collectors
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'run') and
                callable(subclass.run) and
                hasattr(subclass, '_get_data') and
                callable(subclass._get_data) and
                hasattr(subclass, '_process_data') and
                callable(subclass._process_data) and
                hasattr(subclass, '_persist_data') and
                callable(subclass._persist_data) or
                NotImplemented)
        

    @abc.abstractmethod
    def run(self):
        """
        Execute main methods get, process, persist
        """
        raise NotImplementedError
    

    @abc.abstractmethod
    def _get_data(self):
        """
        Get data from social network.
        """
        raise NotImplementedError


    @abc.abstractmethod
    def _process_data(self):
        """
        Process data collected from social network.
        """
        raise NotImplementedError


    @abc.abstractmethod
    def _persist_data(self):
        """
        Persist data processed into database.
        """
        raise NotImplementedError


class Monitor(object):
    
    def __init__(self):
        self._social_network_monitors = [TwitterMonitor]
        # TODO: get list from database, only activated social networks
    
        
    def run(self):
        for snm in self._social_network_monitors:
            snm().run()
            
            
class TwitterMonitor(object):
    
    def __init__(self):
        self._collectors = [TwitterMediaCollector, TwitterStreamCollector]
    
        
    def run(self):
        for collector in self._collectors:
            collector().run()


class Collector(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._dao = MonitorDAO()
        
        
class TwitterCollector(Collector):
    
    def __init__(self):
        super().__init__()
        self._name_social_media = 'twitter'
        self._twitter_api = TwitterAPI()
        self._search_tags = config.MONITOR.SEARCH_TAGS


class TwitterMediaCollector(CollectorInterface, TwitterCollector):
    
    def __init__(self):
        super().__init__()
        self._media_accounts = self._dao.get_media_accounts(self._name_social_media)
        self._logger.info("Twitter Media Collector initialized")

    
    def run(self):
        self._get_data()
        self._process_data()
        self._persist_data()
        
    
    def _get_data(self):
        tags = set(map(str.lower, map(self._normalize_text, self._search_tags)))
        regex_string = '|'.join(tags)
        pattern = re.compile(regex_string)
        for id_social_media_account, screen_name, _, initial_load in self._media_accounts:
            if not initial_load:
                self._logger.info('Updating data from {}'.format(screen_name))
                self._update_data(id_social_media_account, screen_name, pattern)
            else:
                self._logger.info('Fetching data from {}'.format(screen_name))
                self._fetch_data(id_social_media_account, screen_name, pattern, limit=1000)  # TODO: parametrizar limit?
        # TODO: implementar e chamar método disconnect()
        
        
    def _fetch_data(self, id_social_media_account, screen_name, pattern, limit=0, datetime_limit=None):
        """Recupera tweets da timeline da media e armazena em arquivo

        Args:
            id_social_media_account (int): Id da conta da media na rede social
            screen_name (str): Screen name da conta na rede social
            pattern (re.Pattern): Objeto Pattern do módulo re
            limit (int, optional): Quantidade de posts a serem recuperados. \
                Se 0 for passado, serão recuperados os 20 posts mais recentes. \
                Defaults to 0.
            datetime_limit (datetime, optional): Datetime limite do post que deve \
                ser recuperado. Defaults to None.
        """
        
        try:
            tweets = list()
            for status in self._twitter_api.fetch_timeline(screen_name=screen_name, limit=limit):
                tweet = self._process_status(status, id_social_media_account)
                text_post = self._normalize_text(tweet['text_post']).lower()
                if datetime_limit and tweet['datetime_post'] <= datetime_limit:
                    break
                if pattern.search(text_post):
                    tweets.append(tweet)
            if len(tweets):
                self._dao.write_in_pkl(tweets)
        except:
            self._logger.error('Exception while trying colect twitter statuses from {}'.format(screen_name))
            raise
        
    
    def _update_data(self, id_social_media_account, screen_name, pattern):
        last_post_datetime = self._dao.get_last_media_post(id_social_media_account)
        self._fetch_data(id_social_media_account, screen_name, pattern, datetime_limit=last_post_datetime)
        
        
    def _process_data(self):
        pass
    
    
    def _persist_data(self):
        self._logger.info('Persisting data')
        self._dao.insert_posts_from_pkl()
        
        
    def _process_status(self, status, id_social_media_account):
        """
        status: tweepy.models.status - objeto twitter
        """
        
        tweet = dict()
        tweet['text_post'] = ''
        tweet['num_likes'] = 0
        tweet['num_shares'] = 0
        tweet['id_social_media_account'] = id_social_media_account
        tweet['id_post_social_media'] = status.id
        if hasattr(status, "retweeted_status"):  # if is retweet
            tweet['parent_id_post_social_media'] = status.retweeted_status.id
            try:
                tweet['text_post'] = status.retweeted_status.extended_tweet["full_text"]
            except AttributeError:
                tweet['text_post'] = status.retweeted_status.full_text
            finally:
                tweet['num_likes'] = status.retweeted_status.favorite_count
                tweet['num_shares'] = status.retweeted_status.retweet_count
        else:
            tweet['parent_id_post_social_media'] = None
            try:
                tweet['text_post'] = status.extended_tweet["full_text"]
            except AttributeError:
                tweet['text_post'] = status.full_text
        tweet['text_post'] = tweet['text_post'].replace("\n", " ")
        tweet['num_likes'] = status.favorite_count or tweet['num_likes']
        tweet['num_shares'] = status.retweet_count or tweet['num_shares']
        tweet['datetime_post'] = status.created_at
        return tweet
    
    
    def _normalize_text(self, text):
        return normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')


class TwitterStreamStatusProcessor(object):
    
    def __init__(self, name_social_media, dao:MonitorDAO):
        self._dao = dao
        self._name_social_media = name_social_media
        self._media_ids = self._get_media_ids()
    
    
    def process_status(self, status):
        # não armazena posts de medias
        if status.author.id in self._media_ids:
            return
        
        # init
        tweet = dict()

        # social media
        tweet['name_social_media'] = 'twitter'

        # account
        tweet['id_account_social_media'] = status.author.id_str
        tweet['screen_name'] = status.author.screen_name
        tweet['date_creation'] = status.author.created_at
        tweet['blue_badge'] = status.author.verified

        # post
        tweet['id_post_social_media'] = status.id

        if hasattr(status, "retweeted_status"):  # Checa se é retweet
            tweet['parent_id_post_social_media'] = status.retweeted_status.id
        else:
            tweet['parent_id_post_social_media'] = None

        tweet['text_post'] = ''
        tweet['num_likes'] = 0
        tweet['num_shares'] = 0
        if hasattr(status, "retweeted_status"):  # Checa se é retweet
            try:
                tweet['text_post'] = status.retweeted_status.extended_tweet["full_text"]
            except AttributeError:
                tweet['text_post'] = status.retweeted_status.text
            finally:
                tweet['num_likes'] = status.retweeted_status.favorite_count
                tweet['num_shares'] = status.retweeted_status.retweet_count
        else:
            try:
                tweet['text_post'] = status.extended_tweet["full_text"]
            except AttributeError:
                tweet['text_post'] = status.text

        # processa o texto da mensagem.
        tweet['text_post'] = tweet['text_post'].replace("\n", " ")
        # self._preprocessing.process_text(tweet['text_post'])

        # será sempre 0, pois acabou de ser postado
        # tweet['num_likes'] = status.favorite_count
        # será sempre 0, pois acabou de ser postado
        # tweet['num_shares'] = status.retweet_count
        tweet['datetime_post'] = status.created_at

        # if hasattr(status, "retweeted_status"):
        #     print(tweet['text_post'])
        #     print()
        #     print('id tweet:', tweet['id_str'], 'likes:', tweet['num_likes'], 'shares', tweet['num_shares'])
        #     print('parent post id', tweet['parent_id_post'], 'shares:', status.retweeted_status.retweet_count, 'likes:', status.retweeted_status.favorite_count)
        #     # print(tweet['parent_id_post'])
        #     print('#####################################################')
        #     print()

        self._dao.write_in_csv_from_dict(tweet)
        
        
    def _get_media_ids(self):
        self._media_accounts = self._dao.get_media_accounts(self._name_social_media)
        return [media[2] for media in self._media_accounts]


class TwitterStreamCollector(CollectorInterface, TwitterCollector):
    
    def __init__(self):
        super().__init__()
        self.stream_time = config.MONITOR.STREAM_TIME
        self._logger.info("Twitter Streaming initialized.")
        
        
    def run(self):
        self._get_data()
        self._process_data()
        self._persist_data()
        
        
    def _get_data(self):
        """
        docstring
        """
        
        self._logger.info(f'Streaming for {self.stream_time} seconds...')
        self._twitter_api.fetch_stream(self._search_tags, 
                                       self.stream_time, 
                                       TwitterStreamStatusProcessor(self._name_social_media, 
                                                                    self._dao))

    
    def _process_data(self):
        """
        Limpa as notícias capturadas via streaming e persiste os textos processados na coluna 'text_news_cleaned' da tabela 'detectenv.news'.
        """
        self._logger.info("Tratando notícias capturadas via streaming...")

        if self._dao.clean_and_save_text_news():
            self._logger.info("Notícias capturadas via streaming tratadas com sucesso.")  
        else:
             self._logger.info("Nenhuma nova notícia para ser tratada.")
             
    
    def _persist_data(self):
        """
        docstring
        """
        self._logger.info('Persisting data...')
        self._dao.insert_posts()
