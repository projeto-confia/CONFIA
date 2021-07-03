from src.interventor.dao import InterventorDAO
import logging
from src.config import Config as config
from datetime import datetime
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# TODO: refactor to interface and concrete classes, one concrete for each ACF
class Interventor(object):
    
    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._dao = InterventorDAO(config.INTERVENTOR.CURATOR)
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
            if self._is_news_in_fca_data(text_news):
                continue
            row += 1
            self._dao.get_workbook().get_worksheet_by_name('planilha1').write(row, 0, id_news)
            self._dao.get_workbook().get_worksheet_by_name('planilha1').write(row, 1, text_news)
        self._dao.close_workbook()
        
        if config.INTERVENTOR.CURATOR:
            # TODO: changes to SMTP logging
            self._send_curator_mail()
        

    def _send_news_to_agency(self):
        if not self._dao.has_excel_file():
            self._logger.info('There were no news selected to send.')
            return
        
        # TODO: criar módulo python para envio e leitura de e-mail
        self._logger.info("Sending selected news to agency...")
        self._send_mail(self._dao.get_email_from_agency('boatos.org'))
        
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
    
    
    def _send_mail(self, receiver_email):
        
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        
        subject = "[PROJETO CONFIA] - supostas fakes news"
        body = "Este é um e-mail automático enviado pelo ambiente AUTOMATA."

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = config.EMAIL.ACCOUNT
        message["To"] = receiver_email
        message["Subject"] = subject
        # message["Bcc"] = receiver_email  # Recommended for mass emails

        # Add body to email
        message.attach(MIMEText(body, "plain"))

        filename = self._dao.excel_filepath_to_send  # In same directory as script

        # Open file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(config.EMAIL.ACCOUNT, config.EMAIL.PASSWORD)
            server.sendmail(config.EMAIL.ACCOUNT, receiver_email, text)


    def _send_curator_mail(self):
        
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        
        subject = "[PROJETO CONFIA] - has news to be curated"
        body = "Este é um e-mail automático enviado pelo ambiente AUTOMATA."

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = config.EMAIL.ACCOUNT
        message["To"] = config.EMAIL.ACCOUNT
        message["Subject"] = subject
        # message["Bcc"] = receiver_email  # Recommended for mass emails

        # Add body to email
        message.attach(MIMEText(body, "plain"))

        text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(config.EMAIL.ACCOUNT, config.EMAIL.PASSWORD)
            server.sendmail(config.EMAIL.ACCOUNT, config.EMAIL.ACCOUNT, text)