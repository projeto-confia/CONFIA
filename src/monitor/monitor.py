import re
import logging
import numpy as np
import pandas as pd
from src.config import Config as config
from src.monitor.dao import MonitorDAO
from unicodedata import normalize
from src.apis.twitter import TwitterAPI
from src.monitor.interfaces import CollectorInterface, TwitterStatusProcessorInterface
from src.utils.text_preprocessing import TextPreprocessing


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
            
            
class TwitterStatusProcessor(TwitterStatusProcessorInterface):
    
    def __init__(self):
        pass
        
        
    def process(self, status):
        tweet = dict()
        tweet['text_post'] = ''
        tweet['num_likes'] = 0
        tweet['num_shares'] = 0
        tweet['id_post_social_media'] = status.id
        
        if hasattr(status, "retweeted_status"):  # if is a retweet
            
            tweet['parent_id_post_social_media'] = status.retweeted_status.id
            
            try:
                tweet['text_post'] = status.retweeted_status.extended_tweet["full_text"]
            
            except AttributeError:    
                try:
                    tweet['text_post'] = status.retweeted_status.full_text
                except AttributeError:
                    tweet['text_post'] = status.retweeted_status.text
            
            finally:
                tweet['num_likes'] = status.retweeted_status.favorite_count
                tweet['num_shares'] = status.retweeted_status.retweet_count
        
        else:
            tweet['parent_id_post_social_media'] = None
            
            try:
                tweet['text_post'] = status.extended_tweet["full_text"]
            
            except AttributeError:
                try:
                    tweet['text_post'] = status.full_text
                except AttributeError:
                    tweet['text_post'] = status.text
        
        tweet['text_post'] = tweet['text_post'].replace("\n", " ")
        tweet['datetime_post'] = status.created_at
        return tweet
        
        
class TwitterStreamStatusProcessor(TwitterStatusProcessor):
    
    def __init__(self, name_social_network, dao:MonitorDAO, media_ids):
        super().__init__()
        self._name_social_network = name_social_network
        self._dao = dao
        self._media_ids = media_ids
        self._processed_tweets = list()
        self._total_unprocessed_tweets: int = 0
    
    
    def process(self, status):
        if status.author.id in self._media_ids:
            return
        
        tweet = super().process(status)
        
        # checks if the streamed tweet has enough number of shares in order to persist it in the database.
        if tweet["num_shares"] < config.MONITOR.STREAM_FILTER_OF_SHARES:
            self._total_unprocessed_tweets += 1
            return
        
        # TODO: change database name column and table to social_network
        tweet['name_social_media'] = self._name_social_network
        tweet['id_account_social_media'] = status.author.id_str
        tweet['screen_name'] = status.author.screen_name
        tweet['date_creation'] = status.author.created_at
        tweet['blue_badge'] = status.author.verified
        tweet['datetime_post'] = status.created_at
        
        self._processed_tweets.append(tweet)
        
        
    def _store(self):
        self._dao.write_in_pkl(self._processed_tweets)
    
    
class TwitterMediaStatusProcessor(TwitterStatusProcessor):

    def __init__(self):
        super().__init__()
        self.id_social_media_account = None
    
    
    def process(self, status):
        tweet = super().process(status)
        tweet['id_social_media_account'] = self.id_social_media_account
        tweet['num_likes'] = status.favorite_count or tweet['num_likes']
        tweet['num_shares'] = status.retweet_count or tweet['num_shares']
        return tweet


class Collector(CollectorInterface):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._dao = MonitorDAO()
        self._search_tags = config.MONITOR.SEARCH_TAGS
        
        
    def run(self):
        self._get_data()
        self._process_data()
        self._persist_data()
        
        
class TwitterCollector(Collector):
    
    def __init__(self):
        super().__init__()
        self._name_social_network = 'twitter'
        self._media_accounts = self._dao.get_media_accounts(self._name_social_network)
        # print(self._media_accounts)
        self._media_ids = [media[2] for media in self._media_accounts]
        self._twitter_api = TwitterAPI()
        
        
    def _process_data(self):
        self._logger.info('Processing data...')
        df = self._dao._load_pkl()
        if not isinstance(df, pd.DataFrame) or df.empty:
            return
        text_preprocessing = TextPreprocessing()
        df['text_prep'] = df['text_post'].apply(text_preprocessing.text_cleaning)
        df['group'] = pd.Series(range(len(df)))
        df['ratio_similarity'] = 0
        group_col_id = df.columns.get_loc('group')
        ratio_similarity_col_id = df.columns.get_loc('ratio_similarity')
        for index_i, row_i in df.iterrows():
            idx1 = df.iloc[index_i+1:].index
            idx2 = df[df['ratio_similarity'] == 0].index
            idx_intersect = np.intersect1d(idx1, idx2)
            for index_j, row_j in df.iloc[idx_intersect].iterrows():
                is_similar, ratio_similarity = text_preprocessing.check_duplications(row_i['text_prep'], row_j['text_prep'])
                if not is_similar:
                    continue
                df.iloc[index_j, group_col_id] = row_i['group']
                df.iloc[index_j, ratio_similarity_col_id] = ratio_similarity
        self._dao.write_in_pkl(df)


class TwitterMediaCollector(TwitterCollector):
    
    def __init__(self):
        super().__init__()
        self._status_processor = TwitterMediaStatusProcessor()
        self._logger.info("Twitter Media Collector initialized")
        
    
    def _get_data(self):
        tags = set(map(str.lower, map(self._normalize_text, self._search_tags)))
        regex_string = '|'.join(tags)
        pattern = re.compile(regex_string)
        data = list()
        
        for id_social_media_account, screen_name, _, is_reliable, initial_load in self._media_accounts:           
            if not initial_load:
                self._logger.info('Updating data from {}'.format(screen_name))
                data += self._update_data(id_social_media_account, screen_name, is_reliable, pattern)
            else:
                self._logger.info('Fetching data from {}'.format(screen_name))
                data += self._fetch_data(id_social_media_account, screen_name, is_reliable, pattern, limit=1000)  # TODO: parametrize limit?
                            
        if data:
            self._logger.info(f'{len(data)} posts collected from media')
            self._dao.write_in_pkl(data)
        # TODO: Implement and call method disconnect()
        
        
    def _fetch_data(self, id_social_media_account, screen_name, is_reliable, pattern, limit=0, datetime_limit=None):
        """Fetch tweets from account timeline and store in file

        Args:
            id_social_media_account (int): Id of social network account
            screen_name (str): Screen name of the social network account
            pattern (re.pattern): Pattern object from re module
            limit (int, optional): Num of posts to be fetched. \
                If 0 passed, will be fetched 20 posts. Defaults to 0.
            datetime_limit (datetime, optional): Datetime limit of posts datetime publication. Defaults to None.

        Returns:
            list: List of dicts, each dict representing one tweet
        """
        
        try:
            tweets = list()
            self._status_processor.id_social_media_account = id_social_media_account
            
            for status in self._twitter_api.fetch_timeline(screen_name=screen_name, limit=limit):
                tweet = self._status_processor.process(status)
                text_post = self._normalize_text(tweet['text_post']).lower()
                
                if datetime_limit and tweet['datetime_post'] <= datetime_limit:
                    break
                
                if pattern.search(text_post):
                    tweet['is_reliable'] = is_reliable
                    tweets.append(tweet)
                    
            return tweets
        
        except:
            self._logger.error('An exception occurred when trying to collect twitter statuses from {}'.format(screen_name))
            raise
        
    
    def _update_data(self, id_social_media_account, screen_name, is_reliable, pattern):
        last_post_datetime = self._dao.get_last_media_post(id_social_media_account)
        return self._fetch_data(id_social_media_account, screen_name, is_reliable, pattern, datetime_limit=last_post_datetime)
        
        
    def _process_data(self):
        super()._process_data()
    
    
    def _persist_data(self):
        self._logger.info('Persisting data...')
        self._dao.insert_media_posts()
    
    
    def _normalize_text(self, text):
        return normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')


class TwitterStreamCollector(TwitterCollector):
    
    def __init__(self):
        super().__init__()
        self.stream_time = config.MONITOR.STREAM_TIME
        self.status_processor = TwitterStreamStatusProcessor(self._name_social_network,
                                                             self._dao, 
                                                             self._media_ids)
        self._logger.info("Twitter Streaming initialized.")
        
        
    def _get_data(self):
        """
        docstring
        """
        
        self._logger.info(f'Streaming for {self.stream_time} seconds...')
        self._twitter_api.fetch_stream(self._search_tags, 
                                       self.stream_time,
                                       self.status_processor)
        self._logger.info(f'{len(self.status_processor._processed_tweets)} posts collected from streaming.')
        
        if config.MONITOR.STREAM_FILTER_OF_SHARES > 0:
            self._logger.info(f'{self.status_processor._total_unprocessed_tweets} posts collected from streaming did not have at least {config.MONITOR.STREAM_FILTER_OF_SHARES} shares and were rejected.')
            
        self.status_processor._store()

    
    def _process_data(self):
        super()._process_data()
             
    
    def _persist_data(self):
        """
        docstring
        """
        self._logger.info('Persisting data...')
        self._dao.insert_stream_posts()
