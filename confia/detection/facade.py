from confia.detection.detector import Detector

class DetectorFacade:
    def run(self):
        try:
            d = Detector()
        except Exception as e:
            print(str(e))