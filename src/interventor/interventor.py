from src.interventor.dao import InterventorDAO
import logging
from src.config import Config as config


class Interventor(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._dao = InterventorDAO()
        self._logger.info("Interventor initialized.")
    
    
    def select_news_to_be_checked(self):
        """Armazena em arquivo excel as notícias a serem enviadas à ACF
        """
        
        self._logger.info("Selecting news to be checked...")
        
        candidate_news = self._dao.select_candidate_news_to_be_checked(window_size=config.INTERVENTOR.WINDOW_SIZE,
                                                                       prob_classif_threshold=config.INTERVENTOR.PROB_CLASSIF_THRESHOLD,
                                                                       num_records=config.INTERVENTOR.NUM_NEWS_TO_SELECT)
        if not len(candidate_news):
            return
        
        row = 0
        for id_news, text_news in candidate_news:
            if self._is_news_in_fca_data(text_news):
                continue
            row += 1
            self._dao.get_workbook().get_worksheet_by_name('planilha1').write(row, 0, id_news)
            self._dao.get_workbook().get_worksheet_by_name('planilha1').write(row, 1, text_news)
        self._dao.close_workbook()
        

    def send_news_to_agency(self):
        if not self._dao.has_excel_file():
            self._logger.info('There were no news selected to send.')
            return
        
        # TODO: criar módulo python para envio e leitura de e-mail
        self._logger.info("Sending selected news to agency...")
        
        # Registro no banco de dados
        self._logger.info('Persisting sent data...')
        self._dao.persist_excel_in_db()
        
        # TODO: implementar controle de inconsistencia
        # Arquivo enviado, registros não persistidos e vice-versa
        
            
    # TODO: implementar usando o algoritmo de deduplicação
    def _is_news_in_fca_data(self, text_news):
        """Checa se text_news existe na base de dados da ACF
        
        Args:
            text_news (str): Texto da notícia

        Returns:
            bool: True se o texto consta na base de dados, False caso contrário
        """
        return False
