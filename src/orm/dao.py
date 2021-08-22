import pandas as pd
import csv, os
import math
from datetime import datetime
from src.orm.db_wrapper import DatabaseWrapper

class DAO:

    def __init__(self):
        self.__db = DatabaseWrapper()

    def update_news_labels(self, id_news, classification_outcome, ground_truth_label, prob_label):
        """
        Atualiza os atributos 'classification_outcome', 'prob_classification' e 'ground_truth_label' referentes à notícia 'id_news'.
        """
        args = (classification_outcome, ground_truth_label, prob_label, id_news)
        self.__db.execute("UPDATE detectenv.news SET classification_outcome = %s, ground_truth_label = %s, prob_classification = %s where id_news = %s;", args)
        self.__db.commit()

    def get_news_shared_by_users_with_params_ics(self):
        """
        Recupera as notícias compartilhadas por contas de usuário que têm parâmetros 'prob' diferentes de 0.5 computados pelo treinamento do ICS, i.e 
        notícias compartilhadas por usuários com reputação.
        """
        query = "select * from detectenv.get_news_shared_by_users_with_params_ics();"
        news_shared_by_parameterized_ics_users = self.read_query_to_dataframe(query)
        return news_shared_by_parameterized_ics_users
    
    def insert_update_user_accounts_db(self, users):
        i = 1
        aux = -1
        total = len(users.index)

        for _, row in users.iterrows():
            progress = float((i / total) * 100)
            
            if aux != int(progress): 
                aux = int(progress)            
                if aux % 10 == 0 and aux > 0:
                    yield f"Progresso de inserção/atualização de contas de usuário: {aux}%"

            id_social_media             = 2 # TODO: mudar isso quando começarmos a trabalhar com outras redes sociais.
            id_owner                    = None if math.isnan(row["id_owner"]) else int(row["id_owner"])
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
        
        yield "Processo de inserção/atualização de contas de usuários concluído."

    def get_users_which_shared_the_news(self, id_news):
        return self.read_query_to_dataframe(f"select * from detectenv.post p, detectenv.news n, detectenv.social_media_account sma where \
             n.id_news = p.id_news and p.id_social_media_account = sma.id_social_media_account and p.id_news = {id_news}")

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

    def insert_dummy_data_news(self):
        news_df = pd.read_csv(os.path.join(os.getcwd(), "src", "data", "news.csv"), delimiter=';', header=0)

        for _, row in news_df.iterrows():
            id_news                 = int(row["newsId"])
            text_news               = "__@#(#Lorem ipsum dolor sit amet, consectetur adipiscing elit))(#(#))."
            date_time               = str(datetime.now())
            ground_truth_label      = False if id_news <= 300 else True
            text_news_cleaned       = "Lorem ipsum dolor sit amet consectetur adipiscing elit"

            args = (text_news, date_time, None, ground_truth_label, None, text_news_cleaned)
            self.__db.execute("INSERT INTO detectenv.news (text_news, datetime_publication, classification_outcome, ground_truth_label, prob_classification, text_news_cleaned) VALUES (%s, %s, %s, %s, %s, %s);", args)
            self.__db.commit()

    def insert_dummy_data_users(self):
        users_df = pd.read_csv(os.path.join(os.getcwd(), "src", "data", "users.csv"), delimiter=';', header=0)
        i = 1

        for _, row in users_df.iterrows():
            id_original             = int(row["idOriginal"])
            
            args = (1, None, f"TestUser{i}", "2021-08-19", None, 0.5, 0.5, 0.5, 0.5, id_original)
            self.__db.execute("INSERT INTO detectenv.social_media_account (id_social_media, id_owner, screen_name, date_creation, blue_badge, probalphan, probbetan, probumalphan, probumbetan, id_account_social_media) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", args)
            self.__db.commit()
            i += 1

        args = (1, 2, "GloboNews", "2010-05-10", True, None, None, None, None, 142393421)
        self.__db.execute("INSERT INTO detectenv.social_media_account (id_social_media, id_owner, screen_name, date_creation, blue_badge, probalphan, probbetan, probumalphan, probumbetan, id_account_social_media) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", args)
        self.__db.commit()

        args = (1, 1, "RecordNews", "2011-03-1", True, None, None, None, None, 259372253)
        self.__db.execute("INSERT INTO detectenv.social_media_account (id_social_media, id_owner, screen_name, date_creation, blue_badge, probalphan, probbetan, probumalphan, probumbetan, id_account_social_media) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", args)
        self.__db.commit()
    
    def insert_dummy_data_posts(self):
        from random import randint
        posts_df = pd.read_csv(os.path.join(os.getcwd(), "src", "data", "news_users.csv"), delimiter=';', header=0)

        for _, row in posts_df.iterrows():
            id_news                 = int(row["newsId"])
            id_social_media_account = int(row["userId"])
            text_post               = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            date_time               = str(pd.to_datetime(row["date"], dayfirst=True))
            id_post_social_media    = randint(1,100000000000000000)

            args = (id_social_media_account, id_news, None, text_post, 0, 0, date_time, id_post_social_media)
            self.__db.execute("INSERT INTO detectenv.post (id_social_media_account, id_news, parent_id_post_social_media, text_post, num_likes, num_shares, datetime_post, id_post_social_media) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", args)
            self.__db.commit()