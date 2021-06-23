from src.detection.detector import Detector
from src.config import Config as config
import logging

class DetectorFacade:
    """
    docstring
    """
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)

    def run(self):
        try:
            self._logger.info('Running Detector...')
            self._detector = Detector()
            
            if config.DETECTOR.TRAIN_ICS == True:
                self._detector.fit()
            
            self._detector.run()        

            self._logger.info('Detector finished.')
        except:
            raise
    
    def predict(self, id_news_to_be_predicted):
        """
        Faz a predição de uma notícia e retorna o rótulo (0- Não Fake; 1- Fake) e a respectiva probabilidade.
        """
        return self._detector.predict_news(id_news_to_be_predicted)
        
