import re
import tweepy
import abc
import time
import os
import logging
# TODO: transferir authconfig para config.py
import src.monitor.authconfig as cfg
from src.config import Config as config
from src.monitor.dao import MonitorDAO
from unicodedata import normalize


class StreamInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'collect_data') and
                callable(subclass.collect_data) and
                hasattr(subclass, 'process_data') and
                callable(subclass.process_data) and
                hasattr(subclass, 'persist_data') and
                callable(subclass.persist_data) or
                NotImplemented)

    @abc.abstractmethod
    def collect_data(self):
        """
        Coleta dados da rede social.

        Retorna:
            TRUE se não ocorrer falha, FALSE caso contrário.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def process_data(self):
        """
        Processa os dados coletados da rede social.

        Retorna:
            True se não ocorrer falha, False caso contrário.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def persist_data(self):
        """
        Persiste os dados processados na base relacional.

        Retorna:
            True se não ocorrer falha, False caso contrário.
        """
        raise NotImplementedError


class TwitterStreamListener(tweepy.StreamListener):

    def on_connect(self):
        self._dao = MonitorDAO()
        self._tweet_csv_filename = 'tweets.csv'
        self._tweet_csv_path = os.path.join("src", "data", self._tweet_csv_filename)
        # TODO: erro ao criar o arquivo não dispara exceção. Experimentar mover para o init de TwitterStream

    def on_status(self, status):
        """
        status: tweepy.models.status - objeto twitter
        """
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

        self._dao.write_in_csv_from_dict(tweet, self._tweet_csv_path)


class TwitterStream(StreamInterface):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self.streamListener = TwitterStreamListener()
        self._dao = MonitorDAO()
        self.stream_time = config.MONITOR.STREAM_TIME
        self._logger.info("Twitter Streaming initialized.")
    

    def collect_data(self):
        """
        docstring
        """
        
        self._logger.info("Streaming for {} seconds...".format(self.stream_time))
        
        tokens = cfg.tokens
        auth = tweepy.OAuthHandler(
            tokens["consumer_key"], tokens["consumer_secret"])
        auth.set_access_token(
            tokens["access_token"], tokens["access_token_secret"])

        api = tweepy.API(auth)
        streamAccess = tweepy.Stream(
            auth=api.auth, listener=self.streamListener, tweet_mode='extended')
        streamAccess.filter(track=config.MONITOR.SEARCH_TAGS,
                            languages=["pt"],
                            is_async=True)
        time.sleep(self.stream_time)
        streamAccess.disconnect()

    
    def process_data(self):
        """
        docstring
        """
        pass

    
    def persist_data(self):
        """
        docstring
        """
        self._logger.info('Persisting data...')
        self._dao.insert_posts()


class TwitterAPI(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._tokens = cfg.tokens
        self._search_tags = config.MONITOR.SEARCH_TAGS
        self._api = None
        self._dao = MonitorDAO()
        self._name_social_media = 'twitter'
        self._media_accounts = self._dao.get_media_accounts(self._name_social_media)
        
        
    def connect(self):
        if not self._api:
            try:
                auth = tweepy.OAuthHandler(self._tokens['consumer_key'], self._tokens['consumer_secret'])
                auth.set_access_token(self._tokens['access_token'], self._tokens['access_token_secret'])
                self._api = tweepy.API(auth)
            except:
                self._logger.error('Unable to connect to Twitter API.')
                raise
            
    
    # TODO: implementar
    def disconnect(self):
        pass
    
    
    def _normalize_text(self, text):
        return normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')


    def fetch_data(self):
        
        # remover acentos, aplicar lower e transformar a tag list em set
        tags = set(map(str.lower, map(self._normalize_text, self._search_tags)))
        
        # regex pattern from tag list
        regex_string = '|'.join(tags)
        pattern = re.compile(regex_string)
        
        self.connect()
        
        try:
            for id_social_media_account, screen_name in self._media_accounts:
                tweets = list()
                for status in tweepy.Cursor(self._api.user_timeline, 
                                            id=screen_name, 
                                            tweet_mode='extended').items(300):  # TODO: parametrizar a qtd items?
                    # print(status)
                    tweet = self._process_status(status, id_social_media_account)
                    text_post = self._normalize_text(tweet['text_post']).lower()
                    if pattern.search(text_post):
                        tweets.append(tweet)
                        
                if len(tweets):
                    self._dao.write_in_pkl(tweets)
                    
        except:
            self._logger.error('Exception while trying colect twitter statuses from {}'.format(self._media_accounts[0]))
            raise
        
        
    def _process_status(self, status, id_social_media_account):
        """
        status: tweepy.models.status - objeto twitter
        """
        
        # init
        tweet = dict()

        # post
        tweet['id_social_media_account'] = id_social_media_account
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
                tweet['text_post'] = status.retweeted_status.full_text
            finally:
                tweet['num_likes'] = status.retweeted_status.favorite_count
                tweet['num_shares'] = status.retweeted_status.retweet_count
        else:
            try:
                tweet['text_post'] = status.extended_tweet["full_text"]
            except AttributeError:
                tweet['text_post'] = status.full_text

        # processa o texto da mensagem.
        tweet['text_post'] = tweet['text_post'].replace("\n", " ")
        
        # demais atributos
        tweet['num_likes'] = status.favorite_count or tweet['num_likes']
        tweet['num_shares'] = status.retweet_count or tweet['num_shares']
        tweet['datetime_post'] = status.created_at

        return tweet
