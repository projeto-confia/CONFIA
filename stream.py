import tweepy

# class Streaming:


class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print("ID: {0} - @{1} - {2}\n".format(status.author.id, status.author.screen_name, status.text))