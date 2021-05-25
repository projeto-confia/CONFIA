import csv 
import pandas as pd
import numpy as np
import math
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score
from confia.orm.dao import DAO
from time import sleep

class ICS:

    def __init__(self, laplace_smoothing=0.01, omega=0.5):

        self.__dao        = DAO()
        self.__users      = self.__dao.read_query_to_dataframe("select * from detectenv.social_media_account;")
        self.__news       = self.__dao.read_query_to_dataframe("select * from detectenv.news where classification_outcome is not null;")
        self.__news_users = self.__dao.read_query_to_dataframe("select * from detectenv.post;")
        self.__smoothing  = laplace_smoothing
        self.__omega      = omega

    def __init_params(self, test_size = 0.3):

        news = self.__news[self.__news['ground_truth_label'].notnull()]
        if not len(news.index):
            return 0
        
        # divide 'self.__news_users' em treino e teste.
        labels = news["ground_truth_label"]
        self.__X_train_news, self.__X_test_news, _, _ = train_test_split(news, labels, test_size=test_size, stratify=labels)

        # # armazena em 'self.__train_news_users' as notícias compartilhadas por cada usuário.
        self.__train_news_users = pd.merge(self.__X_train_news, self.__news_users, left_on="id_news", right_on="id_news")
        self.__test_news_users  = pd.merge(self.__X_test_news, self.__news_users, left_on="id_news", right_on="id_news")

        # conta a qtde de noticias verdadeiras e falsas presentes no conjunto de treino.
        # TODO: refatorar separando os testes
        try:
            self.__qtd_V = self.__news["ground_truth_label"].value_counts()[0]
            self.__qtd_F = self.__news["ground_truth_label"].value_counts()[1]
        except:
            return 0

        # filtra apenas os usuários que não estão em ambos os conjuntos de treino e teste.
        self.__train_news_users = self.__train_news_users[self.__train_news_users["id_social_media_account"].isin(self.__test_news_users["id_social_media_account"])]

        # inicializa os parâmetros dos usuários.
        totR            = 0
        totF            = 0
        alphaN          = totR + self.__smoothing
        umAlphaN        = ((totF + self.__smoothing) / (self.__qtd_F + self.__smoothing)) * (self.__qtd_V + self.__smoothing)
        betaN           = (umAlphaN * (totR + self.__smoothing)) / (totF + self.__smoothing)
        umBetaN         = totF + self.__smoothing
        probAlphaN      = alphaN / (alphaN + umAlphaN)
        probUmAlphaN    = 1 - probAlphaN
        probBetaN       = betaN / (betaN + umBetaN)
        probUmBetaN     = 1 - probBetaN
        self.__users["probAlphaN"]    = probAlphaN
        self.__users["probUmAlphaN"]  = probUmAlphaN
        self.__users["probBetaN"]     = probBetaN
        self.__users["probUmBetaN"]   = probUmBetaN
        
        return 1
    

    def __assess(self):
        """
        etapa de avaliação: avalia a notícia com base nos parâmetros de cada usuário obtidos na etapa de treinamento.
        """
        predicted_labels = []
        unique_id_news   = self.__test_news_users["id_news"].unique()

        for newsId in unique_id_news:
            # recupera os ids de usuário que compartilharam a notícia representada por 'newsId'.
            usersWhichSharedTheNews = list(self.__news_users["id_social_media_account"].loc[self.__news_users["id_news"] == newsId])

            productAlphaN    = 1.0
            productUmAlphaN  = 1.0
            productBetaN     = 1.0
            productUmBetaN   = 1.0
            
            for userId in usersWhichSharedTheNews:
                i = self.__users.loc[self.__users["id_social_media_account"] == userId].index[0]

                productAlphaN   = productAlphaN  * self.__users.at[i, "probAlphaN"]
                productUmBetaN  = productUmBetaN * self.__users.at[i, "probUmBetaN"]
            
            # inferência bayesiana
            reputation_news_tn = (self.__omega * productAlphaN * productUmAlphaN) * 100
            reputation_news_fn = ((1 - self.__omega) * productBetaN * productUmBetaN) * 100
            
            if reputation_news_tn >= reputation_news_fn:
                predicted_labels.append(0)
            else:
                predicted_labels.append(1)

        # mostra os resultados da matriz de confusão e acurácia.
        gt = self.__X_test_news["ground_truth_label"].tolist()
        print(confusion_matrix(gt, predicted_labels))
        print(accuracy_score(gt, predicted_labels))

    def fit(self, test_size = 0.3):
        """
        Etapa de treinamento: calcula os parâmetros de cada usuário a partir do Implict Crowd Signals.        
        """
        status_code = self.__init_params(test_size)
        if not status_code:
            return 0
        
        i = 0
        users_unique = self.__train_news_users["id_social_media_account"].unique()
        total = len(users_unique)
        
        for userId in users_unique:   
            i = i + 1
            print("", end="Progresso do treinamento: {0:.2f}%\r".format(float((i / total) * 100)), flush=True)
            
            # obtém os labels das notícias compartilhadas por cada usuário.
            newsSharedByUser = list(self.__train_news_users["ground_truth_label"].loc[self.__train_news_users["id_social_media_account"] == userId])
            
            # calcula a matriz de opinião para cada usuário.
            totR        = newsSharedByUser.count(0)
            totF        = newsSharedByUser.count(1)
            alphaN      = totR + self.__smoothing
            umAlphaN    = ((totF + self.__smoothing) / (self.__qtd_F + self.__smoothing)) * (self.__qtd_V + self.__smoothing)
            betaN       = (umAlphaN * (totR + self.__smoothing)) / (totF + self.__smoothing)
            umBetaN     = totF + self.__smoothing

            # calcula as probabilidades para cada usuário.
            probAlphaN      = alphaN / (alphaN + umAlphaN)
            probUmAlphaN    = 1 - probAlphaN
            probBetaN       = betaN / (betaN + umBetaN)
            probUmBetaN     = 1 - probBetaN
            self.__users.loc[self.__users["id_social_media_account"] == userId, "probAlphaN"]   = probAlphaN
            self.__users.loc[self.__users["id_social_media_account"] == userId, "probBetaN"]    = probBetaN
            self.__users.loc[self.__users["id_social_media_account"] == userId, "probUmAlphaN"] = probUmAlphaN
            self.__users.loc[self.__users["id_social_media_account"] == userId, "probUmBetaN"]  = probUmBetaN

        self.__assess()   
        return self.__users

    def predict(self, id_news):
        """
        Classifica uma notícia usando o ICS.
        """

        usersWhichSharedTheNews = self.__dao.get_users_which_shared_the_news(id_news)

        productAlphaN    = 1.0
        productUmAlphaN  = 1.0
        productBetaN     = 1.0
        productUmBetaN   = 1.0
        
        for _, row in usersWhichSharedTheNews.iterrows():
            productAlphaN   = productAlphaN  * row["probalphan"]
            productUmBetaN  = productUmBetaN * row["probumbetan"]
                
        # inferência bayesiana
        reputation_news_tn = (self.__omega * productAlphaN * productUmAlphaN) * 100
        reputation_news_fn = ((1 - self.__omega) * productBetaN * productUmBetaN) * 100

        # calculando o grau de probabilidade da predição.
        total = reputation_news_tn + reputation_news_fn
        prob = 0
        
        if reputation_news_tn >= reputation_news_fn:
            prob = reputation_news_tn / total
            return 0, prob # notícia classificada como legítima.
        else:
            prob = reputation_news_fn / total
            return 1, prob # notícia classificada como fake.