import csv 
import pandas as pd
import numpy as np
import math
from sklearn.model_selection import train_test_split

class User:
    def __init__(self, idUser, sharedNews):
        self.user = idUser
        self.sharedNews = sharedNews
        self.opinion_matrix = np.zeros(shape=(2,2), dtype=int)
        self.probability_matrix = np.zeros(shape=(2,2), dtype=float)

class Detector:
    # A leitura dos arquivos csv é apenas um teste preliminar. Em versões futuras, os dados serão obtidos a partir do BD relacional.
    def __init__(self, users_file="confia/data/users_paulo.csv", news_file = "confia/data/news.csv", 
        news_users_file="confia/data/news_users.csv", laplace_smoothing=0.01):

        self.__users      =    pd.read_csv(users_file, sep=';')
        self.__news       =    pd.read_csv(news_file, sep=';')
        self.__news_users =    pd.read_csv(news_users_file, sep=';')
        self.__smoothing  =    laplace_smoothing

        # atribui uma label para cada notícia. A primeira metade é not fake (0) e a segunda metade é fake (1)
        self.__news["news_label"] = np.array([0, 1])[np.linspace(0,2,len(self.__news), endpoint=False).astype(int)]

        # divide 'self.__news_users' em treino e teste.
        labels = self.__news["news_label"]
        self.__X_train_news, self.__X_test_news, self.__Y_train_news, self.__Y_test_news = train_test_split(
            self.__news, labels, test_size=0.3, stratify=labels)

        # armazena em 'self.__train_news_users' as notícias compartilhadas por cada usuário.
        self.__train_news_users = pd.merge(self.__X_train_news, self.__news_users, on="newsId")
        # armazena em 'self.__test_news_users' as notícias compartilhadas por cada usuário.
        self.__test_news_users = pd.merge(self.__X_test_news, self.__news_users, on="newsId")

        # pega o número total de nóticias 'fake' e 'not fake' em 'self.__train_news_users'.
        self.__num_not_F = self.__train_news_users["news_label"].loc[self.__train_news_users["news_label"] == 0].value_counts()[0]
        self.__num_F = self.__train_news_users["news_label"].loc[self.__train_news_users["news_label"] == 1].value_counts()[1]
        
        # ordena os usuários em ordem crescente.
        self.__train_news_users.sort_values(by=['userId', 'newsId'], inplace=True)

        # ================================================================================================================
        # calcula as métricas para cada usuário.
        userIds = self.__train_news_users["userId"].unique()
        list_users = []

        for userId in userIds:
            # obtém os labels das notícias compartilhadas por cada usuário.
            newsSharedByUser = list(self.__train_news_users["news_label"].loc[self.__train_news_users["userId"] == userId])
            user = User(userId, newsSharedByUser)
            
            # calcula a matriz de opinião para cada usuário.
            totUserR    = newsSharedByUser.count(0)
            totUserF    = newsSharedByUser.count(1)
            alphaN      = totUserR + self.__smoothing
            umBetaN     = totUserF + self.__smoothing
            umAlfaN     = ((totUserF + self.__smoothing) / (self.__num_F + self.__smoothing)) * (self.__num_not_F + self.__smoothing)
            betaN       = (umAlfaN * (totUserR + self.__smoothing)) / (totUserF + self.__smoothing)

            user.opinion_matrix[0,0] = alphaN
            user.opinion_matrix[0,1] = umBetaN
            user.opinion_matrix[1,0] = umAlfaN
            user.opinion_matrix[1,1] = betaN

            # calcula a matriz de probabilidades para cada usuário.
            user.probability_matrix[0,0] = alphaN / (alphaN + umAlfaN)
            user.probability_matrix[0,1] = 1 - user.probability_matrix[0,0]
            user.probability_matrix[1,1] = betaN / (betaN + umBetaN)
            user.probability_matrix[1,0] = 1 - user.probability_matrix[1,1]

            list_users.append(user)
            # print("News shared by user {0}: ".format(userId), newsSharedByUser.values)
            # print("Opinion matrix of user {0}:\n".format(userId), user.opinion_matrix)
            print("Probability matrix of user {0}:\n".format(userId), user.probability_matrix)




        
        
