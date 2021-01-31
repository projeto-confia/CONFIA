import pandas as pd
import csv, os
from datetime import datetime
from confia.orm.db_wrapper import DatabaseWrapper

class DAO:

    def __init__(self):
        self.__db = DatabaseWrapper()
     
    def insert_news_db(self):
        from datetime import datetime

        news = pd.read_csv("confia/data/news.csv", sep=";")
        news["ground_truth_label"] = [0 if newsId <= 300 else 1 for newsId in news["newsId"]]
        
        for _, row in news.iterrows():
            id_news     = int(row["newsId"])
            id_original = str(row["idOriginal"])
            text_news   = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            date_time   = str(datetime.now())
            gt_label    = bool(row["ground_truth_label"])

            args = (id_news, text_news, date_time, None, gt_label, id_original)
            self.__db.execute("INSERT INTO detectenv.news (id_news, text_news, datetime_publication, classification_outcome, ground_truth_label, id_news_original) VALUES (%s, %s, %s, %s, %s, %s);", args)
            self.__db.commit()
    
    def insert_update_user_accounts_db(self, users):
        i = 1
        total = len(users.index)
        for _, row in users.iterrows():
            print("Inserindo/atualizando usuário {0} de {1}...\r".format(i, total), end='', flush=True)

            id_social_media             = 2 # TODO: mudar isso quando começarmos a trabalhar com outras redes sociais.
            id_owner                    = row["id_owner"]
            screen_name                 = str(row["screen_name"])
            date_creation               = row["date_creation"]
            blue_badge                  = row["blue_badge"]
            probAlphaN                  = row["probAlphaN"]
            probUmAlphaN                = row["probUmAlphaN"]
            probBetaN                   = row["probBetaN"]
            probUmBetaN                 = row["probUmBetaN"]
            id_account_social_media     = row["id_account_social_media"]
            
            args = (id_social_media, id_owner, screen_name, date_creation, blue_badge, probAlphaN, probBetaN, probUmAlphaN, probUmBetaN, id_account_social_media)
            self.__db.execute("DO $$ BEGIN PERFORM detectenv.insert_update_social_media_account(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s); END $$;", args)
            self.__db.commit()
            i = i + 1

    def insert_post_db(self, posts):
        from datetime import datetime

        for _, row in posts.iterrows():
            id_social_media_account = int(row["id_social_media_account"])
            id_news                 = int(row["id_news"])
            text_post               = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            date_time               = str(datetime.now())

            args = (id_social_media_account, id_news, None, text_post, 0, 0, date_time)
            self.__db.execute("INSERT INTO detectenv.post (id_social_media_account, id_news, parent_id_post, text_post, num_likes, num_shares, datetime_post) VALUES (%s, %s, %s, %s, %s, %s, %s);", args)
            self.__db.commit()

    def read_query_to_dataframe(self, query):
        return pd.read_sql_query(query, self.__db.connection)

    def read_news_users_from_csv(self, news_users_file="confia/data/news_users.csv"):
        return pd.read_csv(news_users_file, sep=';')

    def write_streaming_tweet_in_csv(self, path_file, tweet, userID):           

        with open(path_file, mode='a') as tweet_file:
            # verifica se o arquivo está vazio para criar o header do csv
            if os.stat(path_file).st_size == 0:
                writer = csv.writer(tweet_file, delimiter=',')
                writer.writerow(["datetime", "userId", "tweet"])    
            
            else:
                now = datetime.now()
                writer = csv.writer(tweet_file, delimiter=',')
                writer.writerow(["{0}:{1}:{2}".format(now.hour, now.minute, now.second), userID, tweet.replace('\n', ' ')])