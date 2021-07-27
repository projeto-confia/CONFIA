from email.mime import text
from src.interventor.dao import InterventorDAO
import logging
from src.config import Config as config
from datetime import datetime
from src.apis.twitter import TwitterAPI
from src.utils.email import EmailAPI


# TODO: refactor to interface and concrete classes, one concrete for each ACF
class Interventor(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._dao = InterventorDAO(config.INTERVENTOR.CURATOR)
        self._twitter_api = TwitterAPI()
        self._email_api = EmailAPI()
        self._logger.info("Interventor initialized.")
        
        
    def run(self):
        if self._is_within_time_window('boatos.org'):
            if config.INTERVENTOR.CURATOR:
                self._send_news_to_agency()  # send possible curated news
            self._select_news_to_be_checked()
            self._send_news_to_agency()
        
        
    def _is_within_time_window(self, agency):
        """Return True if hour and day of week is permitted to agency, False otherwise

        Args:
            agency (str): Name of agency

        Returns:
            boll: True if is in time window, False otherwise
        """
        days_of_week_window = self._dao.get_days_of_week_window(agency)
        days_of_week_window = list(map(str.upper, days_of_week_window))
        today_week = datetime.now().strftime('%A').upper()
        today_hour = datetime.now().hour
        return today_week in days_of_week_window and today_hour > 16  # TODO: parameterize time
    
    
    def _select_news_to_be_checked(self):
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
            is_news_in_fca, fca_url = self._check_news_in_fca_data(text_news)
            if is_news_in_fca:
                self._post_alert(text_news, checked=True, checker='Boatos.org', url=fca_url)
                continue
            row += 1
            self._dao.get_workbook().get_worksheet_by_name('planilha1').write(row, 0, id_news)
            self._dao.get_workbook().get_worksheet_by_name('planilha1').write(row, 1, text_news)
        if row > 0:
            self._dao.close_workbook()
            if config.INTERVENTOR.CURATOR:
                self._send_curator_mail()
        

    def _send_news_to_agency(self):
        if not self._dao.has_excel_file():
            self._logger.info('There were no news selected to send.')
            return
        
        self._logger.info("Sending selected news to agency...")
        self._send_request_mail_to_acf(self._dao.get_email_from_agency('boatos.org'))
        
        # Registro no banco de dados
        self._logger.info('Persisting sent data...')
        self._dao.persist_excel_in_db()
        
        # TODO: implementar controle de inconsistencia
        # Arquivo enviado, registros não persistidos e vice-versa
        
            
    # TODO: implementar usando o algoritmo de deduplicação
    def _check_news_in_fca_data(self, text_news):
        """Check if text_news exists into FCA data
        
        Args:
            text_news (str): Text of the news

        Returns:
            bool: True if text_news exists into FCA data, False otherwise,
            str: If exists, the referencing url within FCA web page.
        """
        
        # return True, 'https://www.boatos.org/saude/ser-infectado-covid-19-protege-7-vezes-mais-que-tomar-qualquer-vacina.html'
        return False, None
    
    
    def _post_alert(self, text_news, checked, checker, url=None):
        if checked:
            header = 'ALERTA: a seguinte notícia foi confirmada como fakenews pela agência {}'.format(checker)
        else:
            header = 'ATENÇÃO: a seguinte notícia foi detectada como suposta fakenews'
            
        text_tweet = header + '\n\n' + text_news + '\n\n' + '{}'.format(url if url else '')
        self._twitter_api.tweet(text_tweet)
    
    
    def _send_request_mail_to_acf(self, acf_email):
        
        text_subject  = 'Supostas fakenews'
        
        text_message  = 'Olá colaborador,\n\n'
        text_message += 'Anexo encontra-se o arquivo Excel com as notícias detectadas pelo AUTOMATA como supostas fakenews.\n\n'
        text_message += 'Agradecemos desde já por sua participação.'
        
        self._email_api.send(to_list=[acf_email], 
                             text_subject=text_subject, 
                             text_message=text_message, 
                             attach_list=[self._dao.excel_filepath_to_send])


    def _send_curator_mail(self):
        
        self._email_api.send(to_list=[config.EMAIL.ACCOUNT],
                             text_subject='Has news to be curated.')
