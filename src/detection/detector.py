# import traceback
import logging
from src.detection.ics import ICS
from src.detection.dao import DAO
from src.config import Config as config

class Detector:

    def __init__(self):
        self._dao = DAO()
        self._ics = ICS(laplace_smoothing=0.01, omega=0.5)
        self._logger = logging.getLogger(config.LOGGING.NAME)

    def run(self):
        
        try:
            self._unlabeled_news_shared_by_reputed_users = self._dao.get_unlabeled_news_shared_by_reputed_accounts()

            if self._unlabeled_news_shared_by_reputed_users.empty:
                self._logger.info("There are no unlabeled news shared by reputed social media accounts.")
            
            else:
                news = set()

                for _, row in self._unlabeled_news_shared_by_reputed_users.iterrows():
                    id_news = row["id_news"]
                    predicted_prob_label = self.predict(id_news)

                    # se algum usuário reputado compartilhou a notícia, ela é atualizada no banco de dados.
                    if predicted_prob_label != (-1, -1):
                        self._dao.update_news_labels(id_news, bool(predicted_prob_label[0]), None, predicted_prob_label[1])
                        news.add(id_news)
                
                if len(news):
                    self._logger.info("The following news were updated:")
                    self._logger.info(f"{sorted(news)}.")
                
                else: self._logger.info("No news were updated.")
        
        except Exception as e:
            self._logger.error(f"An error occurred during the news' updating process: {e.args}")

    def fit(self):
        
        try:
            self._logger.info("Starting the reputation process of social media accounts...")
            self._ics.fit()
        
        except Exception as e:
            self._logger.error(f"An error occurred during the reputation process of social media accounts: {e.args}")

    def predict(self, id_news):
        return self._ics.predict(id_news)

