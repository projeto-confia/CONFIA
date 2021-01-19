import tweepy
import confia.monitor.authconfig as cfg
import confia.monitor.data_access as data
import abc
import time


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
        self.users = data.User()

    def on_status(self, status):
        """
        status: tweepy.models.status - objeto twitter
        """
        # init
        tweet = dict()

        # social media
        tweet['social_media_name'] = 'twitter'

        # account
        tweet['account_id'] = status.author.id_str
        tweet['account_screen_name'] = status.author.screen_name
        tweet['account_date_creation'] = status.author.created_at
        tweet['account_blue_badge'] = status.author.verified

        # post
        tweet['id_str'] = status.id_str

        if hasattr(status, "retweeted_status"):  # Checa se é retweet
            tweet['parent_id_post'] = status.retweeted_status.id_str
        else:
            tweet['parent_id_post'] = None

        tweet['text_post'] = ''
        if hasattr(status, "retweeted_status"):  # Checa se é retweet
            try:
                tweet['text_post'] = status.retweeted_status.extended_tweet["full_text"]
            except AttributeError:
                tweet['text_post'] = status.retweeted_status.text
        else:
            try:
                tweet['text_post'] = status.extended_tweet["full_text"]
            except AttributeError:
                tweet['text_post'] = status.text

        tweet['num_likes'] = status.favorite_count  # será sempre 0, pois acabou de ser postado
        tweet['num_shares'] = status.retweet_count # será sempre 0, pois acabou de ser postado
        tweet['date_time_post'] = status.created_at

        if hasattr(status, "retweeted_status"):
            print(tweet['text_post'])
            print()
            print('id tweet:', tweet['id_str'], 'likes:', tweet['num_likes'], 'shares', tweet['num_shares'])
            print('parent post id', tweet['parent_id_post'], 'shares:', status.retweeted_status.retweet_count, 'likes:', status.retweeted_status.favorite_count)
            # print(tweet['parent_id_post'])
            print('#####################################################')
            print()

        # print("\tID: {0} - @{1} - {2}\n".format(status.author.id, status.author.screen_name, text))
        # self.users.write_in_csv(text, status.author.id)
        

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
        print('vai iniciar o streaming')
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
        pass