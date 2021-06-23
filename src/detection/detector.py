from src.detection.ics import ICS
from src.orm.dao import DAO
from src.config import Config as config
import logging

class Detector:

    def __init__(self):
        self.__ics = ICS(laplace_smoothing=0.01, omega=0.5)
        self.__logger = logging.getLogger(config.LOGGING.NAME)
        self.__dao = DAO()

    def fit(self):
        try:
            self.__logger.info("Iniciando o treinamento do ICS...")
            self.__ics.fit()
        except Exception as e:
            self.__logger.error(f"Ocorreu um erro durante o treinamento do ICS: {e.args}")

    def run(self):
        try:
            # verificando se usuários com reputação (i.e. usuários cujos parâmetros 'prob' diferente de 0.5) compartilharam alguma nova notícia.
            news_shared_by_users_with_params_ics = self.__dao.get_news_shared_by_users_with_params_ics()

            if len(news_shared_by_users_with_params_ics) == 0:
                self.__logger.info("Nenhuma nova notícia compartilhada por usuários reputados.")
            else:
                self.__logger.info("Atualizando notícias compartilhadas por usuários reputados...")
                news = []
                
                for _, row in news_shared_by_users_with_params_ics.iterrows():
                    id_news = row["id_news"]
                    predicted_label, prob_label = self.predict_news(id_news)
                    ground_truth_label = row["ground_truth_label"] 
                    news.append(id_news)

                    # atualiza os labels da notícia 'id_news'.
                    self.__dao.update_news_labels(id_news, bool(predicted_label), ground_truth_label, prob_label)
                
                self.__logger.info("As seguintes notícias foram atualizadas:")
                
                for i in range(len(news)-1):
                    self.__logger.info(f"{news[i]}, ")
                self.__logger.info(f"{news[len(news)-1]}.")

        except Exception as e:
            self.__logger.error(f"Ocorreu um erro durante a atualização das notícias: {e.args}")


    def predict_news(self, id_news):
        label, prob = self.__ics.predict(id_news)
        
        self.__logger.info(f"Notícia {id_news} legítima com probabilidade de {round(prob * 100, 3)}% de acordo com o ICS.") if label == 0 else self.__logger.info(f"Notícia {id_news} falsa com probabilidade de {round(prob * 100, 3)}% de acordo com o ICS.")
        return label, prob
