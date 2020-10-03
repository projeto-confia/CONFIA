import tweepy

if __name__ == "__main__":

    consumer_key = "henwvehuKH6MQtzUbYtGklAWf"
    consumer_secret = "KunYaNThhddSTqTWt6TLSxdkfBIiFoxKrk8MgF5OUqdgDrqSWh"
    access_token = "1176207436119793666-kSr7xfmkR3FCP0XBroqc3AYE8ucGRn"
    access_token_secret = "afN1DR6SGh7JFqQZfAeqz3nnu4ZwZ76rAS44F8u4c6Sh4"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    public_tweets = api.home_timeline()

    for tweet in public_tweets:
        print(tweet.text)