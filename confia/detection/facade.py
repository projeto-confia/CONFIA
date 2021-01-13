from confia.detection.detector import Detector

class DetectorFacade:
    def __init__(self):
        self.__d = Detector()

    def run(self, train_ics=False):
        try:
            if train_ics == False:
               self.__d.train_ics()
            
            print(self.predict(40))

        except Exception as e:
            print(str(e))

    def predict(self, id_news):
        return self.__d.predict_news(id_news)