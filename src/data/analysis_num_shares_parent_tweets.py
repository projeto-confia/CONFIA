from datetime import datetime, timedelta
import tweepy
import pickle, os
import pandas as pd
from typing import List, Tuple
from random import seed, sample
from tweepy.error import TweepError
from src.config import Config as config

DAY_OF_SAMPLING = datetime(2022, 2, 13)

def get_api_twitter() -> tweepy.API:
    """Conecta no Twitter via API utilizando as credenciais do projeto.

    Returns:
        tweepy.API: o objeto para comunicação com a API do Twitter.
    """
    api: tweepy.API = None
    
    try:
        auth = tweepy.OAuthHandler(config.TWITTER_CREDENTIALS.CONSUMER_KEY, config.TWITTER_CREDENTIALS.CONSUMER_SECRET)
        auth.set_access_token(config.TWITTER_CREDENTIALS.ACCESS_TOKEN, config.TWITTER_CREDENTIALS.ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
    
    except Exception as e:
        print(f"An exception has occurred when trying to connect with Twitter: {e.args}")
        
    finally:
        return api
    
def read_csv_file(file_name: str) -> pd.DataFrame:
    """Lê um arquivo .csv e o transforma em um Pandas Dataframe.

    Args:
        file_name (str): o nome do arquivo .csv a ser transformado em Dataframe.

    Returns:
        pd.DataFrame: o Dataframe correspondente ao arquivo .csv passado como argumento.
    """
    return pd.read_csv(f"src/data/{file_name}", header=0, delimiter=',', dtype=str)


def split_df_posts(df_posts: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Recebe o dataframe do snapshot contendo todos os tweets e o reparte em tweets pais e filhos.

    Args:
        df_post (pd.DataFrame): o dataframe referente ao snapshot contendo os tweets coletados via streaming.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (i) dataframe contendo apenas tweets pai; (ii) dataframe contendo apenas tweets filhos.
    """
    
    df_parent_posts = df_posts[~df_posts["parent_id_post_social_media"].notnull()]
    df_children_posts = df_posts[df_posts["parent_id_post_social_media"].notnull()]
    
    return df_parent_posts, df_children_posts


def get_parents_from_children_posts(api: tweepy.API):
    
    """Função responsável por recuperar os tweets pai via API do Twitter a partir do dataframe dos tweets filhos.
    """
    
    if not os.path.exists("src/data/parent_posts_snapshot.csv"):
        
        df_posts = read_csv_file("posts.csv")    
        df_parent_posts, df_children_posts = split_df_posts(df_posts)
        
        # seleciona as colunas importantes.
        df_parent_posts = df_parent_posts[["id_post", "datetime_post", "id_post_social_media", "text_post", "num_shares"]]
        
        # cria um arquivo csv para os tweets pai do snapshot.
        df_parent_posts.to_csv("src/data/parent_posts_snapshot.csv", index=False)
        
    else:
        print(f"File 'parent_posts_snapshot.csv' already exists.")
        
    if not os.path.exists("src/data/parent_posts_recovered.csv"):
        
        parent_tweets_dict = {
            "id_post": [], # row["id_post"]
            "datetime_post": [], # created_at
            "id_post_social_media": [], # id_str
            "text_post": [], # text
            "num_shares": [] # retweet_count
        }
        
        deleted_tweets = []
        
        i = 0
        size = len(df_children_posts)
        
        for _, row in df_children_posts.iterrows():
            
            print(f"Recovering parent tweet from tweet {i+1} of {size}\r", end="")
            
            try:
                id_child_tweet = row["id_post_social_media"]
                parent_id_post_social_media_of_api = api.get_status(id_child_tweet).retweeted_status
                
                parent_tweets_dict["id_post"].append(row["id_post"])
                parent_tweets_dict["datetime_post"].append(parent_id_post_social_media_of_api.created_at)
                parent_tweets_dict["id_social_media_account"].append(parent_id_post_social_media_of_api.id_str)
                parent_tweets_dict["text_post"].append(parent_id_post_social_media_of_api.text)
                parent_tweets_dict["num_shares"].append(parent_id_post_social_media_of_api.retweet_count)
            
            except TweepError as e:
                if int(e.args[0][0]["code"]) == 144:
                    deleted_tweets.append(id_child_tweet)
                    
            finally:
                i += 1
            
        df_parent_posts_api = pd.DataFrame.from_dict(parent_tweets_dict)
        df_parent_posts_api.to_csv("src/data/parent_posts_recovered.csv", index=False)
        
        with open(f"src/data/deleted_tweets.pkl", 'wb') as f:
            pickle.dump(deleted_tweets, f)
            print(f"\n{len(deleted_tweets)} deleted tweets.")
    
    else:
        print(f"File 'parent_posts_recovered.csv' already exists. Skipping recovering process.")
    


def update_num_shares_of_tweets(api: tweepy.API) -> Tuple[pd.DataFrame, List[str]]:
    """Função responsável por atualizar o número de compartilhamentos de cada tweet via API do Twitter.

    Returns:
        o dataframe 'df_parent_posts', contendo o número de compartilhamentos dos tweets pai atualizados.
        a lista de tweets excluídos.        
    """
    
    deleted_tweets = []
    
    df_parent_posts = read_csv_file("parent_posts.csv")
    i = 0
    
    # deixa apenas os tweets pai com até dois dias de publicação.
    df_parent_posts = df_parent_posts[pd.to_datetime(df_parent_posts["datetime_post"]) >= datetime.strptime(df_parent_posts["datetime_post"].max().split(' ')[0], "%Y-%m-%d") - timedelta(days=2)]
    size = len(df_parent_posts)
    
    for index, row in df_parent_posts.iterrows():
        
        id_parent_post = row["id_post_social_media"]
        
        try:
            print(f"Updating number of shares of tweet {i+1}/{size}\r", end="")
            df_parent_posts.loc[index, "num_shares"] = api.get_status(id_parent_post).retweet_count
            
        except TweepError as e:
            if int(e.args[0][0]["code"]) == 144:
                deleted_tweets.append(id_parent_post)
            
        finally:
            i += 1
        
    return df_parent_posts, deleted_tweets
    

def main() -> None:
    
    api = get_api_twitter()
    
    if not api: 
        return
    
    days = (datetime.today() - DAY_OF_SAMPLING).days
    
    get_parents_from_children_posts(api)
    df_parent_posts, deleted_tweets = update_num_shares_of_tweets(api)
    
    df_parent_posts.to_csv(f"src/data/parent_posts_after_{days}_days.csv")
    
    with open(f"src/data/deleted_tweets_after_{days}_days.pkl", 'wb') as f:
        pickle.dump(deleted_tweets, f)


def simple_stats():
    
    day = 1
    
    while day <= 5:
        
        df = pd.read_csv(f"src/data/parent_posts_after_{day}_days.csv")
        sum_of_shares = df["num_shares"].sum()
        
        with open(f"src/data/deleted_tweets_after_{day}_days.pkl", 'rb') as f:
            deleted_tweets = pickle.load(f)
        
        print(f"Day {day} -> shares: {sum_of_shares}; deleted tweets: {len(deleted_tweets)}")
        
        day += 1 

    
if __name__ == "__main__":
    # simple_stats()
    main()
