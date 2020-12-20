import csv 
import pandas as pd
import numpy as np
import math
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score

class Detector:
    # A leitura dos arquivos csv é apenas um teste preliminar. Em versões futuras, os dados serão obtidos a partir do BD relacional.
    def __init__(self, users_file="confia/data/users.csv", news_file = "confia/data/treinoGen2.csv", 
        news_users_file="confia/data/news_users.csv", laplace_smoothing=0.01, omega=0.5):

        self.__users      =    pd.read_csv(users_file, sep=';')
        self.__news       =    pd.read_csv(news_file, sep=';')
        self.__news_users =    pd.read_csv(news_users_file, sep=';')
        self.__smoothing  =    laplace_smoothing
        self.__omega      =    omega

        # atribui uma label para cada notícia. A primeira metade é not fake (0) e a segunda metade é fake (1)
        self.__news["news_label"] = [0 if newsId <= 300 else 1 for newsId in self.__news["newsId"]]
       
        # divide 'self.__news_users' em treino e teste.
        labels = self.__news["news_label"]

        # self.__X_train_news, self.__X_test_news, self.__Y_train_news, self.__Y_test_news = train_test_split(
        #     self.__news, labels, test_size=0.3, stratify=labels)

        # # armazena em 'self.__train_news_users' as notícias compartilhadas por cada usuário.
        # self.__train_news_users = pd.merge(self.__X_train_news, self.__news_users, left_on="newsId", right_on="newsId")
        self.__train_news_users = pd.merge(self.__news, self.__news_users, left_on="newsId", right_on="newsId")
        # print(self.__train_news_users)

        self.__test_news = pd.read_csv("confia/data/testeGen2.csv", sep=';')
        self.__test_news_users = pd.merge(self.__test_news, self.__news_users, left_on="newsId", right_on="newsId")
        # print(self.__test_news_users)

        # conta a qtde de noticias verdadeiras e falsas presentes no conjunto de treino.
        qtd_V = self.__news["news_label"].value_counts()[0]
        qtd_F = self.__news["news_label"].value_counts()[1]

        # filtra apenas os usuários que não estão em ambos os conjuntos de treino e teste.
        self.__train_news_users = self.__train_news_users[self.__train_news_users["userId"].isin(self.__test_news_users["userId"])]
        # print(self.__train_news_users)

        # inicializa os parâmetros dos usuários.
        totR            = 0
        totF            = 0
        alphaN          = totR + self.__smoothing
        umAlphaN        = ((totF + self.__smoothing) / (qtd_F + self.__smoothing)) * (qtd_V + self.__smoothing)
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

        ###############################################################################################
        # etapa de treinamento: calcula os parâmetros de cada usuário a partir do Implict Crowd Signals.
        ###############################################################################################
        
        for userId in self.__train_news_users["userId"].unique():            
            # obtém os labels das notícias compartilhadas por cada usuário.
            newsSharedByUser = list(self.__train_news_users["news_label"].loc[self.__train_news_users["userId"] == userId])
            
            # calcula a matriz de opinião para cada usuário.
            totR        = newsSharedByUser.count(0)
            totF        = newsSharedByUser.count(1)
            alphaN      = totR + self.__smoothing
            umAlphaN    = ((totF + self.__smoothing) / (qtd_F + self.__smoothing)) * (qtd_V + self.__smoothing)
            betaN       = (umAlphaN * (totR + self.__smoothing)) / (totF + self.__smoothing)
            umBetaN     = totF + self.__smoothing

            # calcula as probabilidades para cada usuário.
            probAlphaN      = alphaN / (alphaN + umAlphaN)
            probUmAlphaN    = 1 - probAlphaN
            probBetaN       = betaN / (betaN + umBetaN)
            probUmBetaN     = 1 - probBetaN
            self.__users.loc[self.__users['userId'] == userId, "probAlphaN"]   = probAlphaN
            self.__users.loc[self.__users['userId'] == userId, "probBetaN"]    = probBetaN
            self.__users.loc[self.__users['userId'] == userId, "probUmAlphaN"] = probUmAlphaN
            self.__users.loc[self.__users['userId'] == userId, "probUmBetaN"]  = probUmBetaN

        ###############################################################################################################
        # etapa de avaliação: avalia a notícia com base nos parâmetros de cada usuário obtidos na etapa de treinamento.
        ###############################################################################################################
        self.__test_news["news_label"]      = [0 if newsId <= 300 else 1 for newsId in self.__test_news["newsId"]]
        self.__test_news["predicted_label"] = -1

        for newsId in self.__test_news_users["newsId"].unique():
            # recupera os ids de usuário que compartilharam a notícia representada por 'newsId'.
            usersWhichSharedTheNews = list(self.__news_users["userId"].loc[self.__news_users["newsId"] == newsId])

            productAlphaN    = 1.0
            productUmAlphaN  = 1.0
            productBetaN     = 1.0
            productUmBetaN   = 1.0
            
            for userId in usersWhichSharedTheNews:
                # print(self.__users.loc[self.__users['userId'] == userId])
                i = self.__users.loc[self.__users['userId'] == userId].index[0]

                productAlphaN   = productAlphaN  * self.__users.at[i, "probAlphaN"]
                productUmBetaN  = productUmBetaN * self.__users.at[i, "probUmBetaN"]
            
            # inferência bayesiana
            reputation_news_tn = (self.__omega * productAlphaN * productUmAlphaN) * 100
            reputation_news_fn = ((1 - self.__omega) * productBetaN * productUmBetaN) * 100
            
            if reputation_news_tn >= reputation_news_fn:
                self.__test_news.loc[self.__test_news['newsId'] == newsId, "predicted_label"] = 0
            else:
                self.__test_news.loc[self.__test_news['newsId'] == newsId, "predicted_label"] = 1

        # mostra os resultados da matriz de confusão e acurácia.
        print(confusion_matrix(self.__test_news["news_label"], self.__test_news["predicted_label"]))
        print(accuracy_score(self.__test_news["news_label"], self.__test_news["predicted_label"]))
