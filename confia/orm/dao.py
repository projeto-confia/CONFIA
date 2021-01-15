import csv 
import pandas as pd
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
            print(args)
            self.__db.execute("INSERT INTO detectenv.news (id_news, text_news, datetime_publication, classification_outcome, ground_truth_label, id_news_original) VALUES (%s, %s, %s, %s, %s, %s);", args)
            self.__db.commit()
    
    def insert_update_user_accounts_db(self, users):
        for _, row in users.iterrows():
            id_account      = str(row["id_social_media_account"])
            probAlphaN      = str(row["probAlphaN"])
            probUmAlphaN    = str(row["probUmAlphaN"])
            probBetaN       = str(row["probBetaN"])
            probUmBetaN     = str(row["probUmBetaN"])
            
            args = (id_account, 2, None, None, None, None, probAlphaN, probBetaN, probUmAlphaN, probUmBetaN)
            self.__db.execute("DO $$ BEGIN PERFORM insert_update_social_media_account(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s); END $$;", args)
            self.__db.commit()

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