import logging
import tweepy
import time
import src.monitor.authconfig as cfg
from src.config import Config as config


class TwitterStreamListener(tweepy.StreamListener):
    
    def __init__(self, status_processor):
        super().__init__()
        self._status_processor = status_processor


    def on_status(self, status):
        self._status_processor.process_status(status)
    
    
class TwitterAPI(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._tokens = cfg.tokens
        self._api = None
        self._connect()
        self._logger.info("Twitter API initialized")

        
    def _connect(self):
        if not self._api:
            try:
                auth = tweepy.OAuthHandler(self._tokens['consumer_key'], self._tokens['consumer_secret'])
                auth.set_access_token(self._tokens['access_token'], self._tokens['access_token_secret'])
                self._api = tweepy.API(auth)
            except:
                self._logger.error('Unable to connect to Twitter API.')
                raise
            
    
    # TODO: implementar
    def _disconnect(self):
        pass
    
    
    def fetch_timeline(self, screen_name=None, mode='items', limit=0):
        """Returns the most recent statuses posted from the \
            authenticating user or the screen_name user specified.

        Args:
            screen_name (str, optional): screen name of the user. Defaults to None.
            mode (str, optional): possible values {'items', 'pages'}. Defaults to 'items'.
            limit (int, optional): num of items or pages. Value 0 returns the 20 most recent. Defaults to 0.

        Returns:
            tweepy.Cursor: Tweepy Cursor object
        """
        
        try:
            cursor = tweepy.Cursor(self._api.user_timeline,
                                id=screen_name,
                                tweet_mode='extended')
            if mode == 'items':
                return cursor.items(limit)
            if mode == 'pages':
                return cursor.pages(limit)
        except:
            raise
        
        
    def tweet(self, text_tweet):
        self._api.update_status(text_tweet)
        
        
    def fetch_stream(self, tags, stream_time, status_processor):
        stream_listener = TwitterStreamListener(status_processor)
        streamAccess = tweepy.Stream(auth=self._api.auth, 
                                     listener=stream_listener, 
                                     tweet_mode='extended')
        streamAccess.filter(track=tags,
                            languages=["pt"],
                            is_async=True)
        time.sleep(stream_time)
        streamAccess.disconnect()
