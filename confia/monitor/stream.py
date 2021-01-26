import tweepy
import confia.monitor.authconfig as cfg
import abc
import time
import os
from datetime import datetime
from confia.orm.dao import DAO


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
        self.dao = DAO()

    def on_status(self, status):
        tweet = ""
        if hasattr(status, "retweeted_status"):  # verifica se é um retwwet
            try:
                tweet = status.retweeted_status.extended_tweet["full_text"]
                print(tweet)
            except AttributeError:
                tweet = status.retweeted_status.text
                print(tweet)
        else:
            try:
                tweet = status.extended_tweet["full_text"]
                print("\tID: {0} - @{1} - {2}\n".format(status.author.id, status.author.screen_name, tweet))    
            except AttributeError:
                tweet = status.text
                print("\tID: {0} - @{1} - {2}\n".format(status.author.id, status.author.screen_name, tweet))
        
        tweet = tweet.replace("\n", " ")
        path = os.path.join("confia", "data", datetime.today().strftime('%Y-%m-%d') + ".csv")
        self.dao.write_streaming_tweet_in_csv(path, tweet, status.author.id) 
        

class TwitterStream(StreamInterface):
    def __init__(self):
        self.streamListener = TwitterStreamListener()

    def collect_data(self, interval):
        """
        docstring
        """
        tokens = cfg.tokens
        auth = tweepy.OAuthHandler(tokens["consumer_key"], tokens["consumer_secret"])
        auth.set_access_token(tokens["access_token"], tokens["access_token_secret"])

        api = tweepy.API(auth)
        streamAccess = tweepy.Stream(auth=api.auth, listener=self.streamListener, tweet_mode='extended')
        streamAccess.filter(track=["COVID", "covid", "Covid",  "coronavirus", "coronavírus", "covid-19"], 
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
        pass