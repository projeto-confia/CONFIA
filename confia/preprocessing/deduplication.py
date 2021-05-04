from text_preprocessing import TextPreprocessing
from confia.orm.dao import DAO
from fuzzywuzzy import fuzz
import textdistance
import random
import string
import time
import re

def text_cleaning(raw_tweet):

    # remove hyperlinks, nomes de usuário precedidos pelo '@', pontuações e caracteres especiais.
    tweet = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|''(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', raw_tweet, flags=re.MULTILINE)
    tweet = re.sub("(@[A-Za-z0-9_]+)", "", tweet, flags=re.MULTILINE)
    tweet = re.sub(r"#(\w+)", ' ', tweet, flags=re.MULTILINE)
    tweet = "".join([char.lower() for char in tweet if char not in string.punctuation])
    tweet = re.sub('\s+', ' ', tweet).strip()

    # remove dígitos
    # tweet = re.sub(r"\d", "", tweet)
    return tweet.lower()

if __name__ == "__main__":
    dao = DAO()
    news = dao.read_query_to_dataframe("select * from detectenv.news;")
    news.to_csv(r"confia/data/news.csv", index=True)
    threshold = 70
    similar_tweets = []
    ids = []
    
    # escolhe um id aleatório para fazer a comparação.
    news_idx = random.randint(0, len(news))
    chosen_news = news.iloc[news_idx]["text_news"]
    chosen_news_cleaned = text_cleaning(chosen_news)

    start_time = time.time()

    for i in range(len(news)):
        if i == news_idx: continue
        
        current_news = news.iloc[i]["text_news"]
        current_news = text_cleaning(current_news)
        similarity = fuzz.token_sort_ratio(chosen_news_cleaned, current_news)

        if similarity >= threshold:
            ids.append(news.iloc[i]["id_news"])
            similar_tweets.append(current_news)

    end_time = time.time() - start_time
    
    print(f"\nORIGINAL TWEET: {chosen_news}\n\n{len(similar_tweets)} SIMILAR TWEETS TO: {chosen_news_cleaned}\n\n")
    for i in range(len(similar_tweets)):
        print(f"{ids[i]} -> {similar_tweets[i]}")
    print(f"\nExecution time: {end_time} seconds.")


    
