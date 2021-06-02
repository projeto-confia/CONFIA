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
            self._detector = Detector(config.DETECTOR.TRAIN_ICS)
            self._logger.info('Detector finished.')
        except:
            raise
        
