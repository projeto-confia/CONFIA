from re import S
import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score
from src.detection.dao import DAO
from src.config import Config as config

class ICS:

    def __init__(self, laplace_smoothing=0.01, omega=0.5):
        self.__logger     = logging.getLogger(config.LOGGING.NAME)
        self.__dao        = DAO()
        self.__users      = self.__dao.read_query_to_dataframe("select * from detectenv.social_media_account;")
        self.__news       = self.__dao.read_query_to_dataframe("select * from detectenv.news;")
        self.__news_users = self.__dao.read_query_to_dataframe("select * from detectenv.post;")
        self.__smoothing  = laplace_smoothing
        self.__omega      = omega

        # consulta os id's das contas de veículos de imprensa para filtragem.
        self._press_media_accounts = self.__dao.read_query_to_dataframe("select tbl.id_social_media_account, tbl.id_owner from \
                                    (select * from detectenv.social_media_account where id_owner is not null) tbl, detectenv.owner \
                                    where tbl.id_owner = detectenv.owner.id_owner \
                                    and detectenv.owner.is_media = true and detectenv.owner.is_media_activated = true;")
                                    
        self._press_media_accounts = list(self._press_media_accounts['id_social_media_account'])

    def _fit_initialization(self, test_size = 0.3):
        
        # remove as contas dos veículos de imprensa do treino.
        self.__users = self.__users[~self.__users.id_social_media_account.isin(self._press_media_accounts)]
        self.__news_users = self.__news_users[~self.__news_users.id_social_media_account.isin(self._press_media_accounts)]

        labeled_news = self.__news[self.__news['ground_truth_label'].notnull()]
        labels = labeled_news["ground_truth_label"]
        print(f"QTD LABELS: {len(labels)}")

        # se não tem amostras rotuladas no dataset, retorna uma exceção
        if len(labeled_news) == 0:
            self.__logger.info('Não há notícias rotuladas para realizar o treinamento do ICS.')
            return 0
        
        else: # divide 'self.__news_users' em treino e teste.
            try:
                self.__X_train_news, self.__X_test_news, _, _ = train_test_split(labeled_news, labels, test_size=test_size, stratify=labels)
                print(f"LENGTH X_TRAIN_NEWS: {self.__X_train_news}\nLENGTH X_TEST_NEWS: {self.__X_test_news}")
            except:
                self.__logger.info("Não há amostras rotuladas o suficiente para treinar o ICS.")
                return 0

            # armazena em 'self.__train_news_users' as notícias compartilhadas por cada usuário.
            self.__train_news_users = pd.merge(self.__X_train_news, self.__news_users, left_on="id_news", right_on="id_news")
            print(f"FIT train_news_users: {self.__train_news_users}")
            self.__test_news_users  = pd.merge(self.__X_test_news, self.__news_users, left_on="id_news", right_on="id_news")
            print(f"FIT test_news_users: {self.__test_news_users}")

            # conta a quantidade de noticias verdadeiras e falsas presentes no conjunto de treino.
            try:
                self.__qtd_V = self.__train_news_users["ground_truth_label"].value_counts()[0]
                print(f"QTD_V: {self.__qtd_V}")
            except:
                self.__logger.info("Não há notícias rotuladas como 'não fake (0)' para realizar o treinamento do ICS.")
                return 0
            try:
                self.__qtd_F = self.__train_news_users["ground_truth_label"].value_counts()[1]
                print(f"QTD_F: {self.__qtd_F}")
            except:
                self.__logger.info("Não há notícias rotuladas como 'fake (1)' para realizar o treinamento do ICS.")
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
        self.__test_news_users = self.__test_news_users[self.__test_news_users["ground_truth_label"].notnull()]
        print(f"ASSESS test_news_users: {self.__test_news_users}")
        unique_id_news   = self.__test_news_users["id_news"].unique()

        for newsId in unique_id_news:
            # recupera os id's de usuário que compartilharam a notícia representada por 'newsId'.
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
        self.__logger.info(f"Desempenho do ICS no conjunto de teste:\nMatriz de confusão:\n{confusion_matrix(gt, predicted_labels)}")
        self.__logger.info(f"Acurácia: {accuracy_score(gt, predicted_labels)}")

    def fit(self, test_size = 0.3):
        """
        Etapa de treinamento: calcula os parâmetros de cada usuário a partir do Implict Crowd Signals.        
        """
        if self._fit_initialization(test_size) == 1:
            i = 0
            users_unique = self.__train_news_users["id_social_media_account"].unique()
            total = len(users_unique)
            aux = -1
            
            for userId in users_unique:   
                i = i + 1
                progress = float((i / total) * 100)
                
                if aux != int(progress): 
                    aux = int(progress)
                
                    if aux % 20 == 0 and aux > 0:
                        self.__logger.info(f"Progresso do treinamento: {aux}%")
                
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
            
            self.__logger.info("Treinamento concluído.")
            # self.__assess()  
       
            self.__logger.info("Salvando os parâmetros de usuário no banco de dados...")
            try:
                for msg in self.__dao.insert_update_user_accounts_db(self.__users):
                    self.__logger.info(msg)

                self.__logger.info("Parâmetros dos usuários salvos com sucesso!\n")
            except Exception as e:
                raise Exception(f"Ocorreu um erro ao salvar os parâmetros de usuário no banco de dados.\n{e.args}")
        else:
            self.__logger.info("Não foi possível treinar o ICS.")

    def predict(self, id_news):
        """
        Classifica uma notícia usando o ICS.
        """
        usersWhichSharedTheNews = self.__dao.get_users_which_shared_the_news(id_news)

        if not usersWhichSharedTheNews.empty:

            usersWhichSharedTheNews = usersWhichSharedTheNews.loc[:, ~usersWhichSharedTheNews.columns.duplicated()]
           
            # removendo as contas dos veículos de imprensa.
            usersWhichSharedTheNews = usersWhichSharedTheNews[(~usersWhichSharedTheNews["id_social_media_account"].isin(self._press_media_accounts))]

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
        else:
            return -1, -1
        