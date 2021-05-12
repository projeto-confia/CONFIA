from confia.interventor.dao import InterventorDAO


class Interventor(object):
    
    def __init__(self):
        self._dao = InterventorDAO()
    
    
    def select_news_to_check(self):
        """Armazena em arquivo excel as notícias a serem enviadas à ACF

        Returns:
            boll: True se há notícias, False caso contrário
        """
        candidate_news = self._dao.select_candidate_news_to_check()
        if not len(candidate_news):
            return False
        row = 1
        for id_news, text_news in candidate_news:
            if self._is_news_in_fca_data(text_news):
                continue
            self._dao.get_workbook().get_worksheet_by_name('planilha1').write(row, 0, id_news)
            self._dao.get_workbook().get_worksheet_by_name('planilha1').write(row, 1, text_news)
            row += 1
        self._dao.close_workbook()
        return True
            

    def send_news_to_agency(self):
        # TODO: criar módulo python para envio e leitura de e-mail
        print('\tSending mail...')
        
        # Registro no banco de dados
        self._dao.persist_excel_in_db()
        
        # TODO: implementar controle de inconsistencia
        # Arquivo enviado, registros não persistidos e vice-verdadeiras
    
            
    # TODO: implementar usando o algoritmo de deduplicação
    def _is_news_in_fca_data(self, text_news):
        """Checa se text_news existe na base de dados da ACF
        
        Args:
            text_news (str): Texto da notícia

        Returns:
            bool: True se o texto consta na base de dados, False caso contrário
        """
        return False
