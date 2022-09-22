import xlsxwriter
import numpy as np
import pandas as pd
from pathlib import Path
from jobs.job import Job
from datetime import datetime
from typing import List, Optional
import os, shutil, pathlib, pickle
from src.config import Config as config
from src.orm.db_wrapper import DatabaseWrapper
from src.utils.singleton import SingletonMetaClass


class InterventorDAO(metaclass=SingletonMetaClass):
    
    def __init__(self):
        self.excel_filepath_to_send = os.path.join('src', 'data', 'acf', 'to_send', 'confia.xlsx')
        self._excel_filepath_sent = os.path.join('src', 'data', 'acf', 'to_send', 'sent')
        self._excel_filepath_to_curator = os.path.join('src', 'data', 'acf', 'to_curator', 'confia.xlsx')
        self._curator = config.INTERVENTOR.CURATORSHIP
    
    
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
        
        sql_string =   "select n.id_news, n.text_news, n.classification_outcome \
                        from detectenv.news n inner join detectenv.post p on p.id_news = n.id_news \
                                            left join detectenv.checking_outcome co on co.id_news = n.id_news \
                                            left join detectenv.curatorship cur on cur.id_news = n.id_news \
                        where n.datetime_publication > current_date - interval '" + str(window_size) + "' day \
                            and n.ground_truth_label is null \
                            and n.classification_outcome is not null \
                            and co.datetime_sent_for_checking is null \
                            and co.id_news is null \
                            and cur.id_news is null \
                            and cur.is_news is null \
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
        
        
    def persist_to_curatorship(self, id_news: int, id_news_checked: Optional[int]):
        sql_string = "INSERT INTO detectenv.curatorship \
                (id_news, id_news_checked) \
                VALUES (%s,%s);"
        try:
            with DatabaseWrapper() as db:
                db.execute(sql_string, (id_news, id_news_checked))
        except:
            raise
        
        
    def persist_similar_news(self, similars):
        sql_string_1 = "INSERT INTO detectenv.similarity_checking_outcome \
                        (id_news, id_news_checked) \
                        VALUES (%s,%s);"
        sql_string_2 = "UPDATE detectenv.news \
                        SET ground_truth_label = true \
                        WHERE id_news = %s;"
        try:
            with DatabaseWrapper() as db:
                for id_news, _, _, id_news_checked in similars:
                    db.execute(sql_string_1, (id_news, id_news_checked))
                    db.execute(sql_string_2, (id_news, ))
        except:
            raise
        
        
    def persist_candidates_to_check(self, id_news, id_trusted_agency):
        sql_string = "INSERT INTO detectenv.checking_outcome \
                        (id_news, id_trusted_agency) \
                        VALUES (%s,%s);"
        try:
            with DatabaseWrapper() as db:
                db.execute(sql_string, (id_news, id_trusted_agency))
        except:
            raise
        
    
    def check_whether_there_are_fca_email_jobs_in_pkl(self):
        
        pkl_file = pathlib.Path('jobs/interventor_jobs.pkl')
        
        if pkl_file.exists():
            
            with open(pathlib.Path('jobs/interventor_jobs.pkl'), 'rb') as file:
                interventor_jobs = pickle.load(file)
                
                for _, job_manager in interventor_jobs.items():
                    if config.SCHEDULE.QUEUE[job_manager.job.queue] == config.SCHEDULE.QUEUE.INTERVENTOR_SEND_NEWS_TO_FCA:
                        return True
        
        return False
    
        
    def update_time_when_the_news_was_sent_to_fca(self, id_news: int, id_trusted_agency: int) -> None:
        sql_string = "UPDATE detectenv.checking_outcome \
                        SET datetime_sent_for_checking = %s \
                        WHERE id_news = %s and id_trusted_agency = %s;"
        try:
            with DatabaseWrapper() as db:
                db.execute(sql_string, (datetime.now(), id_news, id_trusted_agency, ))
        except:
            raise
        
        
    def get_data_from_agency(self, agency_name):
        """Get Trusted Agency data

        Args:
            agency_name (str): Name of trusted agency

        Returns:
            tuple: Trusted Agency data like (id, email, name, days_of_week)
        """
        
        sql_string = "select ta.id_trusted_agency, ta.email_agency, ta.name_agency, ta.days_of_week \
                    from detectenv.trusted_agency ta \
                    where upper(ta.name_agency) = upper(%s);"
        try:
            with DatabaseWrapper() as db:
                record = db.query(sql_string, (agency_name,))
            return record[0]
        except:
            raise
        
        
    def get_id_and_name_of_trusted_agency_by_its_email_address(self, email_address: str) -> int:
        sql_string = "SELECT id_trusted_agency, name_agency \
                        FROM detectenv.trusted_agency \
                        WHERE email_agency = %s;"
        try:
            with DatabaseWrapper() as db:
                record = db.query(sql_string, (email_address,))
            return record[0]
        except:
            raise
        
        
    def get_curations(self):
        """Get curations already curated but not processed

        Returns:
            list: list of tuples like (id_news, text_news, id_news_checked, is_fake_news, is_similar, id_curatorship)
        """
        
        sql_string = "SELECT cur.id_news, n.text_news, cur.id_news_checked, cur.is_fake_news, cur.is_similar, cur.id_curatorship \
                        FROM detectenv.curatorship cur inner join detectenv.news n on cur.id_news = n.id_news \
                        WHERE not cur.is_processed \
                            and cur.is_curated"
        try:
            with DatabaseWrapper() as db:
                records = db.query(sql_string)
            return records
        except:
            raise


    def close_curations(self, curations_id):
        """Set curations records as processed

        Args:
            curations_id (tuple): tuple of int. Ids of curatorship
        """
        
        sql_string = "UPDATE detectenv.curatorship \
                        SET is_processed = true \
                        WHERE id_curatorship in %s;"
        try:
            with DatabaseWrapper() as db:
                db.execute(sql_string, (curations_id, ))
        except:
            raise
        
        
    def get_all_agency_news(self):
        
        sql_string = "SELECT anc.id_news_checked, anc.publication_title, anc.id_trusted_agency \
                        FROM detectenv.agency_news_checked anc"
        try:
            with DatabaseWrapper() as db:
                records = db.query(sql_string)
            
            return records
        
        except:
            raise
        
        
    def get_agency_name_and_url_of_checked_news(self, id_checked_news: int) -> tuple[str]:
        sql_string = "SELECT anc.publication_url, ta.name_agency \
                        FROM detectenv.agency_news_checked anc, detectenv.trusted_agency ta \
                        WHERE id_news_checked = %s and anc.id_trusted_agency = ta.id_trusted_agency;"
        try:
            with DatabaseWrapper() as db:
                record = db.query(sql_string, (id_checked_news,))
            return record[0]
        
        except:
            raise
        
        
    def update_ground_truth_label(self, news):
        sql_string = "UPDATE detectenv.news \
                        SET ground_truth_label = %s \
                        WHERE id_news = %s;"
        try:
            with DatabaseWrapper() as db:
                for id_news, label in news:
                    db.execute(sql_string, (label, id_news))
        except:
            raise
        
    
    @staticmethod
    def build_excel_spreadsheet(candidates_to_check: list[tuple[int, str]]) -> tuple[str, str]:
        """Build an excel file containing the candidate news to be sent and checked by the FCAs.

        Args:
            candidates_to_check (list[tuple[int, str]): list of candidate news to be checked.
        """
        file_name = Path(f"{config.INTERVENTOR.PATH_NEWS_TO_SEND_AS_EXCEL_SHEET_TO_FCAs}", f"{datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M:%S')}_noticias_candidatas_para_ACF.xlsx")
        
        df_news = pd.DataFrame(candidates_to_check, columns=["identificador", "noticia_a_ser_checada"])
        df_news["É Fake? (Sim/Não)"] = np.NaN
        df_news["Link ou referência da ACF"] = np.NaN
        
        df_news.rename(columns={"identificador": "Identificador", "noticia_a_ser_checada": "Notícia a ser checada"}, inplace=True)
        
        sheet_name = "Noticias para Checagem"
        
        with pd.ExcelWriter(file_name, engine='xlsxwriter', mode='w') as writer:
            df_news.to_excel(writer, sheet_name=sheet_name, startrow=2, index=False)

            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # add the title to the excel.
            worksheet.write(0,0, f"NOTÍCIAS PARA CHECAGEM - {datetime.strftime(datetime.now(), '%d/%m/%Y')}", \
                workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'}))
            
            # format main header
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter', 'font_size': 14, 'fg_color': '#FDE9D9'})
            
            worksheet.merge_range('A1:D2', f"NOTÍCIAS PARA CHECAGEM - {datetime.strftime(datetime.now(), '%d/%m/%Y')}", merge_format)
            
            # formats the header of the excel.
            header_format = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'center', 'valign': 'vcenter', 'border': 1})
            
            for col_num, value in enumerate(df_news.columns.values):
                worksheet.write(2, col_num, value, header_format)
                
            # add border to the table.
            border_fmt = workbook.add_format({'bottom':1, 'top':1, 'left':1, 'right':1})
            worksheet.conditional_format(xlsxwriter.utility.xl_range(0, 0, len(df_news)+2, len(df_news.columns)-1), {'type': 'no_errors', 'format': border_fmt})
            
            # center the values of the worksheet, except the second.
            format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
            format_news_col = workbook.add_format({'align': 'left', 'text_wrap': True, 'valign': 'vcenter'})
            
            # set column widths.
            worksheet.set_column(0, 0, 16, format)
            worksheet.set_column(1, 1, 125, format_news_col)
            worksheet.set_column(2, 3, 30, format)
            
            # set row heights.
            for row_num in range(3, len(candidates_to_check) + 3):
                worksheet.set_row(row_num, 35)
                
        return f"Spreadsheet containing the candidate news to be sent to FCAs has been generated successfully in {file_name}.", str(file_name.resolve())
        
        
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
    
    
    def get_clean_text_news_from_id(self, id_news: int) -> str:
        """Returns the cleaned text of a news given its id.

        Args:
            id_news (int): the id of the news.

        Returns:
            str: the news' clean content.
        """
        try:
            sql_str = "select text_news_cleaned from detectenv.news where id_news = %s;"
            
            with DatabaseWrapper() as db:
                text_cleaned = db.query(sql_str, (id_news,))
            
            return text_cleaned[0][0]
        
        except:
            raise
        
    
    def get_all_distinct_id_news_from_checking_outcome(self) -> list[int]:
        try:
            sql_str = "select distinct id_news from detectenv.checking_outcome;"
            
            with DatabaseWrapper() as db:
                news_ids = db.query(sql_str, ())
            
            return news_ids
        
        except:
            raise