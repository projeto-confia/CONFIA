from src.detection.ics import ICS
from src.detection.dao import DAO
from src.config import Config as config
import logging

class Detector:

    def __init__(self):
        self._dao = DAO()
        self._ics = ICS(laplace_smoothing=0.01, omega=0.5)
        self._logger = logging.getLogger(config.LOGGING.NAME)

    def run(self):
        
        try:
            self._unlabeled_news_shared_by_reputed_users = self._dao.get_unlabeled_news_shared_by_reputed_users()

            if self._unlabeled_news_shared_by_reputed_users.empty:
                self._logger.info("There are no unlabeled news shared by reputed social media accounts.")
            
            else:
                news = set()

                for i, row in self._unlabeled_news_shared_by_reputed_users:
                    id_news = row["id_news"]
                    predicted_label, prob_label = self.predict(id_news)

                    if predicted_label != -1 and prob_label != -1:
                        self._dao.update_news_labels(id_news, bool(predicted_label), None, prob_label)
                        news.add(id_news)
                
                if len(news):
                    self._logger.info("The following news were updated:")
                    self._logger.info(f"{news}.")
        
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

