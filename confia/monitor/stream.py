import tweepy
import abc
import time
import os
from datetime import datetime
import confia.monitor.authconfig as cfg
from confia.orm.dao import DAO
from confia.monitor.dao import MonitorDAO
from confia.monitor.preprocessing import TextPreprocessing


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
    def collect_data(self, interval: int):
        """
        Coleta dados da rede social.

        Parâmetros:
            interval (int) - Tempo em segundos para a coleta de dados.

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
        # self._preprocessing = TextPreprocessing()
        self._dao = MonitorDAO()
        self._tweet_csv_filename = 'tweets.csv'
        self._tweet_csv_path = os.path.join(
            "confia", "data", self._tweet_csv_filename)

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
        self.streamListener = TwitterStreamListener()
        self._dao = MonitorDAO()

    def collect_data(self, interval):
        """
        docstring
        """
        tokens = cfg.tokens
        auth = tweepy.OAuthHandler(
            tokens["consumer_key"], tokens["consumer_secret"])
        auth.set_access_token(
            tokens["access_token"], tokens["access_token_secret"])

        api = tweepy.API(auth)
        streamAccess = tweepy.Stream(
            auth=api.auth, listener=self.streamListener, tweet_mode='extended')
        streamAccess.filter(track=["COVID", "covid", "Covid",  "coronavirus", "coronavírus", "covid-19", "vacina"],
                            languages=["pt"],
                            is_async=True)
        time.sleep(interval)
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
        self._dao.insert_posts()
