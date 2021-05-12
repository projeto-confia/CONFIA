import xlsxwriter
import os
from confia.interventor.dao import InterventorDAO


class Interventor(object):
    
    def __init__(self):
        self._dao = InterventorDAO()
        self._workbook = None
    
    
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
            self._get_workbook().get_worksheet_by_name('planilha1').write(row, 0, id_news)
            self._get_workbook().get_worksheet_by_name('planilha1').write(row, 1, text_news)
            row += 1
        self._workbook.close()
        self._workbook = None
        return True
            

    def send_news_to_agency(self):
        print('\tsending news to agency now')
        # simular o envio do arquivo
        # inserir no banco os registros na tabela checking_outcome
            # cuidado especial para o controle de inconsistencia
            # ou seja, arquivo ser enviado mas registros não serem persistidos no banco
    
            
    # TODO: implementar usando o algoritmo de deduplicação
    def _is_news_in_fca_data(self, text_news):
        """Checa se text_news existe na base de dados da ACF
        
        Args:
            text_news (str): Texto da notícia

        Returns:
            bool: True se o texto consta na base de dados, False caso contrário
        """
        return False
        
    
    def _get_workbook(self):
        if not self._workbook:
            workbook = xlsxwriter.Workbook(os.path.join('confia', 'data', 'confia.xlsx'))
            bold = workbook.add_format({'bold': True})
            text_wrap = workbook.add_format({'text_wrap': True})
            worksheet = workbook.add_worksheet('planilha1')
            worksheet.set_column(1, 1, 100, text_wrap)
            worksheet.write(0, 0, 'Id', bold)
            worksheet.write(0, 1, 'Texto', bold)
            self._workbook = workbook
        return self._workbook