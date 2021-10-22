import math
import logging
import pandas as pd
from src.detection.dao import DAO
from src.config import Config as config

class ICS:

    def __init__(self, laplace_smoothing=0.01, omega=0.5):
        self._dao = DAO()
        self._omega = omega
        self._smoothing = laplace_smoothing
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._press_media_accounts_ids = self._dao.get_list_of_ids_press_media_accounts()

    def predict(self, id_news):

        # aqui já são removidas as contas dos veículos de imprensa.
        df_reputed_users_which_shared_the_news = self._dao.get_users_which_shared_the_news(id_news, all_users=False)

        if not df_reputed_users_which_shared_the_news.empty:

            productAlphaN    = 1.0
            productUmAlphaN  = 1.0
            productBetaN     = 1.0
            productUmBetaN   = 1.0

            for _, row in df_reputed_users_which_shared_the_news.iterrows():
                productAlphaN   = productAlphaN  * row["probalphan"]
                productUmBetaN  = productUmBetaN * row["probumbetan"]

            # inferência bayesiana.
            reputation_news_tn = (self._omega * productAlphaN * productUmAlphaN) * 100
            reputation_news_fn = ((1 - self._omega) * productBetaN * productUmBetaN) * 100

            # calculando o grau de probabilidade da predição.
            prob = 0
            total = reputation_news_tn + reputation_news_fn
            
            if reputation_news_tn >= reputation_news_fn:
                prob = reputation_news_tn / total
                return (0, prob) # notícia classificada como legítima.

            else:
                prob = reputation_news_fn / total
                return (1, prob) # notícia classificada como fake.

        else:
            return (-1, -1) # nenhum usuário reputado compartilhou a notícia.

    def fit(self):

        df_labeled_news = self._dao.get_labeled_news()
        list_social_media_accounts = []
        # l = 0
        
        if df_labeled_news.empty:
            self._logger.info("There are no labeled news to repute social media accounts.")

        else:
            qtd_V = len(df_labeled_news.loc[df_labeled_news["ground_truth_label"] == False])
            qtd_F = len(df_labeled_news.loc[df_labeled_news["ground_truth_label"] == True])
            
            #TODO: Início da paralelismo

            for _, row_labeled_news in df_labeled_news.iterrows():

                id_news = row_labeled_news["id_news"]
                df_users_which_shared_the_news = self._dao.get_users_which_shared_the_news(id_news, all_users=True)

                if not df_users_which_shared_the_news.empty:

                    for j, _ in df_users_which_shared_the_news.iterrows():

                        id_social_media_account = df_users_which_shared_the_news.loc[j,"id_social_media_account"][0]
                        df_news_shared_by_the_user = self._dao.get_labels_of_news_shared_by_user(id_social_media_account)

                        # calcula a matriz de opinião para cada usuário.
                        # total de notícias 'not fake' compartilhadas pelo usuário.
                        totR        = len(df_news_shared_by_the_user.loc[df_news_shared_by_the_user["ground_truth_label"] == False]) 
                        # total de notícias 'fake' compartilhadas pelo usuário.
                        totF        = len(df_news_shared_by_the_user.loc[df_news_shared_by_the_user["ground_truth_label"] == True])
                        
                        alphaN      = totR + self._smoothing
                        umAlphaN    = ((totF + self._smoothing) / (qtd_F + self._smoothing)) * (qtd_V + self._smoothing)
                        betaN       = (umAlphaN * (totR + self._smoothing)) / (totF + self._smoothing)
                        umBetaN     = totF + self._smoothing

                        # calcula as probabilidades para cada usuário.
                        probAlphaN      = alphaN / (alphaN + umAlphaN)
                        probUmAlphaN    = 1 - probAlphaN
                        probBetaN       = betaN / (betaN + umBetaN)
                        probUmBetaN     = 1 - probBetaN

                        df_users_which_shared_the_news.loc[j, "probalphan"]   = probAlphaN
                        df_users_which_shared_the_news.loc[j, "probbetan"]    = probBetaN
                        df_users_which_shared_the_news.loc[j, "probumalphan"] = probUmAlphaN
                        df_users_which_shared_the_news.loc[j, "probumBetan"]  = probUmBetaN

                        tuple_social_media_accounts = (1, #TODO: alterar isso quando trabalharmos com mais redes sociais.
                                df_users_which_shared_the_news.loc[j,"id_owner"],
                                df_users_which_shared_the_news.loc[j,"screen_name"],
                                str(df_users_which_shared_the_news.loc[j,"date_creation"]),
                                df_users_which_shared_the_news.loc[j,"blue_badge"],
                                df_users_which_shared_the_news.loc[j,"probalphan"],
                                df_users_which_shared_the_news.loc[j,"probbetan"],
                                df_users_which_shared_the_news.loc[j,"probumalphan"],
                                df_users_which_shared_the_news.loc[j,"probumbetan"],
                                df_users_which_shared_the_news.loc[j,"id_account_social_media"],
                                id_social_media_account
                            )

                        list_social_media_accounts.append(tuple_social_media_accounts)
                    
            #TODO: Fim do paralelismo.
                # l+=1                
                # if l>500: break

            self._logger.info("Social media accounts have been reputed successfully!")       
            self._logger.info("Saving probabilities in database...")

            try:
                self._dao.update_social_media_accounts(list_social_media_accounts)
                self._logger.info("Social media accounts' probabilities saved successfully!")

            except Exception as e:
                self._logger.error(f"An error occurred when updating social media accounts' probabilities in database: {e.args}")