from confia.detection.detector import Detector

class DetectorFacade:
    def __init__(self, train_ics=True):
        self.__d = Detector(train_ics)

    def run(self):    
        self.__d.predict_news(40)