import tweepy

class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print("@{0} - {1}\n".format(status.author.screen_name, status.text))