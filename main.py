import tweepy
import stream
import authconfig as cfg

def primeiroAcesso():
    tokens = cfg.tokens
    auth = tweepy.OAuthHandler(tokens["consumer_key"], tokens["consumer_secret"])
    auth.set_access_token(tokens["access_token"], tokens["access_token_secret"])

    api = tweepy.API(auth)
    public_tweets = api.home_timeline()

    for tweet in public_tweets:
        print(tweet.text)

def exemploStreaming():
    tokens = cfg.tokens
    streamListener = stream.StreamListener()
    auth = tweepy.OAuthHandler(tokens["consumer_key"], tokens["consumer_secret"])
    auth.set_access_token(tokens["access_token"], tokens["access_token_secret"])

    api = tweepy.API(auth)
    streamAccess = tweepy.Stream(auth=api.auth, listener=streamListener)
    streamAccess.filter(track=["COVID", "covid", "Covid",  "coronavirus", "coronavírus", "covid-19"], languages=["pt"])

if __name__ == "__main__":
    exemploStreaming()

    