from src.config import Config as config
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailAPI(object):
    
    def __init__(self, ssl_port=465, smtp_server='smtp.gmail.com') -> None:
        super().__init__()
        self._ssl_port = ssl_port
        self._smtp_server = smtp_server
        self._sender_name = 'Projeto CONFIA'
        
        
    def send(self, to_whom : list[str], text_subject: str, text_message : str = None, \
            attachment_list : list[str] = None, cc_list: list[str] = None, bcc_list: list[str] = None):
        """Sends an email using gmail account

        Args:
            to_whom (list): list of recipients;
            text_subject (str): text to be added to email subject field;
            text_message (str, optional): text to be added to email body. Defaults to None;
            attachment_list (list, optional): list of path to files to be attached. Defaults to None;
            cc_list (list, optional): list of Carbon Copy recipients. Defaults to None;
            bcc_list (list, optional): list of Blind Carbon Copy recipients. Defaults to None.
        """
        
        subject = '[PROJETO CONFIA] - '
        subject += text_subject
        
        body = "Este é um e-mail automático enviado pelo ambiente AUTOMATA.\n\n"
        if text_message:
            body += text_message

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = self._sender_name
        message["To"] = ', '.join(to_whom)
        message["Subject"] = subject
        
        recipients = to_whom
        if cc_list:
            message["Cc"] = ', '.join(cc_list)
            recipients = recipients + cc_list
        if bcc_list:
            recipients = recipients + bcc_list
            
        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        # attach files
        if attachment_list:
            
            for filename in attachment_list:
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
        
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL(self._smtp_server, self._ssl_port, context=context) as server:
            try:
                server.login(config.EMAIL.ACCOUNT, config.EMAIL.PASSWORD)
                server.send_message(message, config.EMAIL.ACCOUNT, recipients)
            except:
                raise
