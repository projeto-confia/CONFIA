from confia.interventor.dao import InterventorDAO


class Interventor(object):
    
    def __init__(self):
        self._dao = InterventorDAO()
    
    
    def select_news_to_check(self):
        candidate_news = self._dao.select_candidate_news_to_check()
        print(candidate_news)
        
    
    def send_news_to_agency(self):
        print('\tsending news to agency now')