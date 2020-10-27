import tweepy
import authconfig as cfg
from DAO import data_access as data

class StreamListener(tweepy.StreamListener):

    def on_connect(self):
        self.users = data.User()

    def on_status(self, status):
        if self.users.is_user_in_dataset(status.author.id):
            print("ID: {0} - @{1} - {2}\n".format(status.author.id, status.author.screen_name, status.text))
            self.users.count_similar_users += 1

            print("Number of database users found in streaming: {0}".format(self.users.count_similar_users))  
            self.users.write_in_csv(status.text, status.author.id, self.users.count_similar_users)     
        

class Streaming:
    def __init__(self):
        self.streamListener = StreamListener()

    def runStreaming(self):
        tokens = cfg.tokens
        auth = tweepy.OAuthHandler(tokens["consumer_key"], tokens["consumer_secret"])
        auth.set_access_token(tokens["access_token"], tokens["access_token_secret"])

        api = tweepy.API(auth)
        streamAccess = tweepy.Stream(auth=api.auth, listener=self.streamListener)
        streamAccess.filter(track=["COVID", "covid", "Covid",  "coronavirus", "coronavírus", "covid-19"], languages=["pt"])