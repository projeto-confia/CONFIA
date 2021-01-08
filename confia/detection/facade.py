from confia.detection.detector import Detector

class DetectorFacade:
    def run(self):
        try:
            d = Detector()
            d.train_ics()
        except Exception as e:
            print(str(e))