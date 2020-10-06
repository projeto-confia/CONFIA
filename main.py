import tweepy
import stream
import authconfig as cfg

def primeiroAcesso():
    tokens = cfg.tokens
    auth = tweepy.OAuthHandler(tokens["consumer_key"], tokens["consumer_secret"])
    auth.set_access_token(tokens["access_token"], tokens["access_token_secret"])

    api = tweepy.API(auth)
    followers = api.followers()
    api.send_direct_message(recipient_id=3243420285, text="Isso é um teste!")

    for f in followers:
        print(f.screen_name+ " - " + f.name + " - " + str(f.id))
    # for f in followers:
    #     print(f.author.name)

def exemploStreaming():
    tokens = cfg.tokens
    streamListener = stream.StreamListener()
    auth = tweepy.OAuthHandler(tokens["consumer_key"], tokens["consumer_secret"])
    auth.set_access_token(tokens["access_token"], tokens["access_token_secret"])

    api = tweepy.API(auth)
    streamAccess = tweepy.Stream(auth=api.auth, listener=streamListener)
    streamAccess.filter(track=["COVID", "covid", "Covid",  "coronavirus", "coronavírus", "covid-19"], languages=["pt"])

if __name__ == "__main__":
    primeiroAcesso()
    # exemploStreaming()

    # 3243420285
    # 3243420285