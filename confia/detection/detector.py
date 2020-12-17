import csv 
import pandas as pd
import numpy as np
import math
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score

class User:
    def __init__(self, idUser, sharedNews):
        self.id = idUser
        self.sharedNews = sharedNews
        self.opinion_matrix = np.zeros(shape=(2,2), dtype=float)
        self.probability_matrix = np.zeros(shape=(2,2), dtype=float)

class Detector:
    # A leitura dos arquivos csv é apenas um teste preliminar. Em versões futuras, os dados serão obtidos a partir do BD relacional.
    def __init__(self, users_file="confia/data/users.csv", news_file = "confia/data/treinoGen1.csv", 
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
        print(self.__train_news_users)

        self.__test_news = pd.read_csv("confia/data/testeGen1.csv", sep=';')
        self.__test_news_users = pd.merge(self.__test_news, self.__news_users, left_on="newsId", right_on="newsId")
        print(self.__test_news_users)

        # conta a qtde de noticias verdadeiras e falsas presentes no conjunto de treino.
        qtd_V = self.__news["news_label"].value_counts()[0]
        qtd_F = self.__news["news_label"].value_counts()[1]

        # filtra apenas os usuários que não estão em ambos os conjuntos de treino e teste.
        self.__train_news_users = self.__train_news_users[self.__train_news_users["userId"].isin(self.__test_news_users["userId"])]
        print(self.__train_news_users)

        # inicializa os parâmetros dos usuários.
        totR = 0
        totF = 0
        self.__users["alphaN"]      = totR + self.__smoothing
        self.__users["betaN"]       = ((totF + self.__smoothing) / (qtd_F + self.__smoothing)) * (qtd_V + self.__smoothing)
        self.__users["umAlphaN"]    = (self.__users["betaN"] * (totR + self.__smoothing)) / (totF + self.__smoothing)
        self.__users["umBetaN"]      = totF + self.__smoothing

        print(self.__users)
        print(self.__news["news_label"].value_counts())












        # # # faz o balanceamento das amostras a partir da quantidade de amostras menor entre ambas as classes.
        # g = self.__train_news_users.groupby('news_label')
        # self.__train_news_users = pd.DataFrame(g.apply(lambda x: x.sample(g.size().min()).reset_index(drop=True)))

        # # armazena em 'self.__test_news_users' as notícias compartilhadas por cada usuário.
        # self.__test_news_users = pd.merge(self.__X_test_news, self.__news_users, left_on="newsId", right_on="newsId")

        # # pega o número total de nóticias 'fake' e 'not fake' em 'self.__train_news_users'.
        # self.__num_not_F = self.__train_news_users["news_label"].value_counts()[0]
        # self.__num_F = self.__train_news_users["news_label"].value_counts()[1]
        
        # # ordena os usuários dos conjuntos de treino e teste em ordem crescente.
        # self.__train_news_users.sort_values(by=['userId', 'newsId'], inplace=True)
        # self.__test_news_users.sort_values(by=['userId', 'newsId'], inplace=True)

        # # ================================================================================================================
        # # calcula as métricas para cada usuário.
        # userIds = self.__train_news_users["userId"].unique()
        # dict_users  = {}

        # for userId in userIds:
        #     # obtém os labels das notícias compartilhadas por cada usuário.
        #     newsSharedByUser = list(self.__train_news_users["news_label"].loc[self.__train_news_users["userId"] == userId])
        #     user = User(userId, newsSharedByUser)
            
        #     # calcula a matriz de opinião para cada usuário.
        #     totUserR    = newsSharedByUser.count(0)
        #     totUserF    = newsSharedByUser.count(1)
        #     alphaN      = totUserR + self.__smoothing
        #     umBetaN     = totUserF + self.__smoothing
        #     umAlfaN     = ((totUserF + self.__smoothing) / (self.__num_F + self.__smoothing)) * (self.__num_not_F + self.__smoothing)
        #     betaN       = (umAlfaN * (totUserR + self.__smoothing)) / (totUserF + self.__smoothing)

        #     user.opinion_matrix[0,0] = alphaN
        #     user.opinion_matrix[0,1] = umBetaN
        #     user.opinion_matrix[1,0] = umAlfaN
        #     user.opinion_matrix[1,1] = betaN

        #     # calcula a matriz de probabilidades para cada usuário.
        #     user.probability_matrix[0,0] = alphaN / (alphaN + umAlfaN)          # probAlfaN
        #     user.probability_matrix[1,0] = 1 - user.probability_matrix[0,0]     # probUmAlfaN
        #     user.probability_matrix[1,1] = betaN / (betaN + umBetaN)            # probBetaN
        #     user.probability_matrix[0,1] = 1 - user.probability_matrix[1,1]     # probUmBetaN

        #     dict_users[user.id] = user
        #     # print("News shared by user {0}: ".format(userId), newsSharedByUser.values)
        #     # print("Opinion matrix of user {0}:\n".format(userId), user.opinion_matrix)
        #     # print("Probability matrix of user {0}:\n".format(userId), user.probability_matrix)

        # # ================================================================================================================
        # # avaliando as notícias de teste
        # self.__test_news_users["predicted_label"] = -1
        # i = 0

        # for _, news in self.__test_news_users.iterrows():
        #     productAlfaN = 1
        #     productUmAlfaN = 1
        #     productBetaN = 1
        #     productUmBetaN = 1

        #     try:
        #         user = dict_users[news["userId"]]
        #     except:
        #          # obtém os labels das notícias compartilhadas por cada usuário.
        #         user = User(news["userId"], [])
                
        #         # calcula a matriz de opinião para cada usuário.
        #         totUserR    = 0
        #         totUserF    = 0
        #         alphaN      = totUserR + self.__smoothing
        #         umBetaN     = totUserF + self.__smoothing
        #         umAlfaN     = ((totUserF + self.__smoothing) / (self.__num_F + self.__smoothing)) * (self.__num_not_F + self.__smoothing)
        #         betaN       = (umAlfaN * (totUserR + self.__smoothing)) / (totUserF + self.__smoothing)

        #         user.opinion_matrix[0,0] = alphaN
        #         user.opinion_matrix[0,1] = umBetaN
        #         user.opinion_matrix[1,0] = umAlfaN
        #         user.opinion_matrix[1,1] = betaN

        #         # calcula a matriz de probabilidades para cada usuário.
        #         user.probability_matrix[0,0] = alphaN / (alphaN + umAlfaN)          # probAlfaN
        #         user.probability_matrix[1,0] = 1 - user.probability_matrix[0,0]     # probUmAlfaN
        #         user.probability_matrix[1,1] = betaN / (betaN + umBetaN)            # probBetaN
        #         user.probability_matrix[0,1] = 1 - user.probability_matrix[1,1]     # probUmBetaN

        #     productAlfaN    = productAlfaN   * user.probability_matrix[0,0]
        #     productUmBetaN  = productUmBetaN * user.probability_matrix[0,1]

        #     # inferência bayesiana
        #     reputation_news_vn = (self.__omega * productAlfaN * productUmAlfaN) * 100
        #     reputation_news_fn = ((1 - self.__omega) * productBetaN * productUmBetaN) * 100
            
        #     if reputation_news_vn >= reputation_news_fn:
        #         self.__test_news_users._set_value(i, "predicted_label", 0)
        #     else:
        #         self.__test_news_users._set_value(i, "predicted_label", 1)
            
        #     i = i + 1

        # # deleta do dataframe os id's dos usuários que não foram encontrados no conjunto de treino. 
        # # self.__test_news_users.drop(self.__test_news_users.loc[self.__test_news_users["predicted_label"] == -1].index, inplace=True)                

        # # mostra os resultados da matriz de confusão e acurácia.
        # print(confusion_matrix(self.__test_news_users["news_label"], self.__test_news_users["predicted_label"]))
        # print(accuracy_score(self.__test_news_users["news_label"], self.__test_news_users["predicted_label"]))
