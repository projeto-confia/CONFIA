import csv 
import pandas as pd

class Detector:
    # A leitura dos arquivos csv é apenas um teste preliminar. Em versões futuras, os dados serão obtidos a partir do BD relacional.
    def __init__(self, users_file="confia/data/users_paulo.csv", news_file = "confia/data/news.csv", 
        news_users_file="confia/data/news_users.csv"):

        self.__users =      pd.read_csv(users_file, sep=';')
        self.__news =       pd.read_csv(news_file, sep=';')
        self.__news_users = pd.read_csv(news_users_file, sep=';')
            
        # print(self.__news_users.values)


