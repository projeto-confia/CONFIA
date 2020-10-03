import tweepy

class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print("{0}".format(status.text))