import os, shutil
import pandas as pd
import xlsxwriter
from datetime import datetime
from src.orm.db_wrapper import DatabaseWrapper


class InterventorDAO(object):
    
    def __init__(self, curator):
        self.excel_filepath_to_send = os.path.join('src', 'data', 'acf', 'to_send', 'confia.xlsx')
        self._excel_filepath_sent = os.path.join('src', 'data', 'acf', 'to_send', 'sent')
        self._excel_filepath_to_curator = os.path.join('src', 'data', 'acf', 'to_curator', 'confia.xlsx')
        self._curator = curator
        self._workbook = None
    
    
    def select_news_to_be_verified(self,
                                   window_size=7,
                                   prob_classif_threshold=0.9,
                                   num_records=4):
        """Select news to be verified
        
        News will be query in database according function parameters.
        The query will sort records by num_shares, prob_classification.
        The top num_records will be returned.

        Args:
            window_size (int, optional): Num days before current day to filter datetime_publications. Defaults to 7.
            prob_classif_threshold (float, optional): Threshold to filter publications by prob_classification. Defaults to 0.9.
            num_records (int, optional): Num of records to get. Defaults to 4.

        Returns:
            list: list of news
        """
        
        sql_string =   "select n.id_news, n.text_news \
                        from detectenv.news n left join detectenv.checking_outcome co on co.id_news = n.id_news \
                                            inner join detectenv.post p on p.id_news = n.id_news \
                        where n.datetime_publication > current_date - interval '" + str(window_size) + "' day \
                            and n.ground_truth_label is null \
                            and n.classification_outcome = True \
                            and co.id_news is null \
                            and n.prob_classification > " + str(prob_classif_threshold) + " \
                        group by n.id_news, n.text_news, n.prob_classification \
                        order by max(p.num_shares) desc, n.prob_classification desc \
                        limit " + str(num_records) + ";"
        
        try:
            with DatabaseWrapper() as db:
                records = db.query(sql_string)
            return records
        except:
            raise
        
    
    def get_workbook(self):
        try:
            if not self._workbook:
                path = self.excel_filepath_to_send if not self._curator else self._excel_filepath_to_curator
                workbook = xlsxwriter.Workbook(path)
                bold = workbook.add_format({'bold': True})
                text_wrap = workbook.add_format({'text_wrap': True})
                worksheet = workbook.add_worksheet('planilha1')
                worksheet.set_column(1, 1, 100, text_wrap)
                worksheet.set_column(2, 2, 20, text_wrap)
                worksheet.set_column(3, 3, 100, text_wrap)
                worksheet.write(0, 0, 'Id', bold)
                worksheet.write(0, 1, 'Texto', bold)
                worksheet.write(0, 2, 'Checagem', bold)
                worksheet.write(0, 3, 'Link', bold)
                self._workbook = workbook
            return self._workbook
        except:
            raise
        
        
    def close_workbook(self):
        self._workbook.close()
        self._workbook = None
        
        
    def persist_excel_in_db(self):
        
        try:
            df = pd.read_excel(self.excel_filepath_to_send, 'planilha1', engine='openpyxl')
            ids = df['Id'].tolist()
            # TODO: datetime deve ser do envio do e-mail
            dt = datetime.now()

            args = ((id, 1, dt) for id in ids)
            sql_string = "INSERT INTO detectenv.checking_outcome \
                            (id_news, id_trusted_agency, datetime_sent_for_checking) \
                            VALUES (%s,%s,%s);"

            with DatabaseWrapper() as db:
                for tup in args:
                    db.execute(sql_string, tup)
                    
            shutil.move(self.excel_filepath_to_send, os.path.join(self._excel_filepath_sent, '{}.xlsx'.format(datetime.now())))
            
        except:
            raise
        
        
    def has_excel_file(self):
        return os.path.exists(self.excel_filepath_to_send)
    
    
    def get_days_of_week_window(self, agency):
        
        sql_string = "select ta.days_of_week \
                    from detectenv.trusted_agency ta \
                    where upper(ta.name_agency) = upper(%s);"
        
        try:
            with DatabaseWrapper() as db:
                record = db.query(sql_string, (agency,))
            return record[0][0].split(',')
        except:
            raise
        
        
    def get_email_from_agency(self, agency):
        
        sql_string = "select ta.email_agency \
                    from detectenv.trusted_agency ta \
                    where upper(ta.name_agency) = upper(%s);"
        
        try:
            with DatabaseWrapper() as db:
                record = db.query(sql_string, (agency,))
            return record[0][0]
        except:
            raise


    def register_fca_similar_news(self, id_news, id_news_checked):
        
        sql_string_1 = "INSERT INTO detectenv.similarity_checking_outcome \
                        (id_news, id_news_checked) \
                        VALUES (%s,%s);"
                        
        sql_string_2 = "UPDATE detectenv.news \
                        SET ground_truth_label = true \
                        WHERE id_news = %s;"

        
        try:
            with DatabaseWrapper() as db:
                db.execute(sql_string_1, (id_news, id_news_checked))
                db.execute(sql_string_2, (id_news, ))
        except:
            raise


    def register_log_alert(self, id_news, status):
        """Register log alert in database

        Args:
            id_news (int): Primary key of news
            status (str): Type of alert. Admitted values are 'similar' or 'detected'
        """
        try:
            if status not in ('similar', 'detected'):
                raise
            action_type_name = 'alert_similar' if status == 'similar' else 'alert_detected'
            dt = datetime.now()
            sql_string = "INSERT INTO detectenv.action_log \
                        (id_action, id_news, datetime_log, description_log) \
                        VALUES ((SELECT act.id_action \
                                FROM detectenv.action_type act \
                                WHERE upper(act.name_action) = upper(%s)), \
                                %s, %s, 'alerta registrado no twitter');"
                                
            with DatabaseWrapper() as db:
                db.execute(sql_string, (action_type_name, id_news, dt))
        except:
            raise


    def get_news_from_excel(self):
        try:
            df = pd.read_excel(self.excel_filepath_to_send, 'planilha1', engine='openpyxl')
            df.drop(columns=['Checagem', 'Link'], inplace=True)
            df.set_index('Id', inplace=True)
            return df.to_dict(orient='index')
        except:
            raise
