import csv 
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

class Detector:
    # A leitura dos arquivos csv é apenas um teste preliminar. Em versões futuras, os dados serão obtidos a partir do BD relacional.
    def __init__(self, users_file="confia/data/users_paulo.csv", news_file = "confia/data/news.csv", 
        news_users_file="confia/data/news_users.csv"):

        self.__users =      pd.read_csv(users_file, sep=';')
        self.__news =       pd.read_csv(news_file, sep=';')
        self.__news_users = pd.read_csv(news_users_file, sep=';')

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

        # from collections import Counter
        # print(Counter(self.__train_news_users.loc[self.__train_news_users["userId"] == 1]["userId"]))
        # print(self.__train_news_users.loc[self.__train_news_users["userId"] == 1])

        # ordena os usuários em ordem crescente.
        self.__train_news_users.sort_values(by=['userId', 'newsId'], inplace=True)
        print(self.__train_news_users)






    def __get_train_test_sets(self):
        pass
        
