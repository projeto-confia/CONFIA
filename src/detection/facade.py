from src.detection.detector import Detector
from src.config import Config as config
import logging

class DetectorFacade:
    """
    docstring
    """
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._logger.setLevel(logging.INFO) 

    def run(self, id_news_to_be_predicted=-1):
        try:
            self._logger.info('Running Detector...')
            self._detector = Detector()
            
            if config.DETECTOR.TRAIN_ICS == True:
                self._detector.fit()
            
            self._detector.run()

            if id_news_to_be_predicted != -1:
                self._detector.predict_news(id_news_to_be_predicted)

            self._logger.info('Detector finished.')
        except:
            raise
        
