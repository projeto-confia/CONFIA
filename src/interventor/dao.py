import os
import pandas as pd
import xlsxwriter
from datetime import datetime
from src.orm.db_wrapper import DatabaseWrapper


class InterventorDAO(object):
    
    def __init__(self):
        self._excel_file_path = os.path.join('src', 'data', 'confia.xlsx')
        self._workbook = None
    
    
    def select_candidate_news_to_be_checked(self, 
                                            window_size=7, 
                                            prob_classif_threshold=0.9, 
                                            num_records=4):
        """Select candidate news to be send to Fact Check Agencys
        
        Candidate news will be query in database according function parameters.
        The query will sort records by num_shares, prob_classification.
        The top num_records will be returned.

        Args:
            window_size (int, optional): Num days before current day to filter datetime_publications. Defaults to 7.
            prob_classif_threshold (float, optional): Threshold to filter publications by prob_classification. Defaults to 0.9.
            num_records (int, optional): Num of records to get. Defaults to 4.

        Returns:
            list: list of candidates
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
                workbook = xlsxwriter.Workbook(self._excel_file_path)
                bold = workbook.add_format({'bold': True})
                text_wrap = workbook.add_format({'text_wrap': True})
                worksheet = workbook.add_worksheet('planilha1')
                worksheet.set_column(1, 1, 100, text_wrap)
                worksheet.write(0, 0, 'Id', bold)
                worksheet.write(0, 1, 'Texto', bold)
                self._workbook = workbook
            return self._workbook
        except:
            raise
        
        
    def close_workbook(self):
        self._workbook.close()
        self._workbook = None
        
        
    def persist_excel_in_db(self):
        
        try:
            df = pd.read_excel(self._excel_file_path, 'planilha1', engine='openpyxl')
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
                    
            os.remove(self._excel_file_path)
            
        except:
            raise
