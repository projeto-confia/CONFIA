import xlsxwriter
import numpy as np
import pandas as pd
from typing import List
from pathlib import Path
from jobs.job import Job
from datetime import datetime
import os, shutil, pathlib, pickle
from src.config import Config as config
from src.orm.db_wrapper import DatabaseWrapper

class Singleton(type):
    """Creates a singleton object for the InterventorDAO class.

    Returns:
        InterventorDAO: the same singleton object if it has been already created. Otherwise, it creates a new one.
    """
    
    _instances = {}

    def __call__(cls, *args, **kwargs):
        
        if cls not in cls._instances:
            
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
            
        return cls._instances[cls]


class InterventorDAO(metaclass=Singleton):
    
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
        
        sql_string =   "select n.id_news, n.text_news \
                        from detectenv.news n inner join detectenv.post p on p.id_news = n.id_news \
                                            left join detectenv.checking_outcome co on co.id_news = n.id_news \
                                            left join detectenv.curatorship cur on cur.id_news = n.id_news \
                        where n.datetime_publication > current_date - interval '" + str(window_size) + "' day \
                            and n.ground_truth_label is null \
                            and n.classification_outcome = True \
                            and co.datetime_sent_for_checking is null \
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
        
        
    def persist_to_curatorship(self, news):
        sql_string = "INSERT INTO detectenv.curatorship \
                (id_news, id_news_checked) \
                VALUES (%s,%s);"
        try:
            with DatabaseWrapper() as db:
                for id_news, _, id_news_checked in news:
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
                for id_news, _, id_news_checked in similars:
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
    
        
    def update_the_time_when_the_news_was_sent_to_fca(self, id_news: int, id_trusted_agency: int) -> None:
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
    
    def get_interventor_job(self, id_job: int) -> tuple[str]:
        try:
            sql_str = "select * from detectenv.job where id_job = %s;"
            
            with DatabaseWrapper() as db:
                job = db.query(sql_str, (id_job,))
            
            return job[0]
        
        except:
            raise
    
    
    def get_failed_interventor_job(self, id_job: int) -> tuple[str]:
        try:
            sql_str = "select * from detectenv.failed_job where id_job = %s;"
            
            with DatabaseWrapper() as db:
                job = db.query(sql_str, (id_job,))
            
            return job[0]
        
        except:
            raise
    
    
    
    def get_all_interventor_jobs(self) -> List[Job]:
        """Selects from Job table all the jobs regarding the Interventor module.
            
        Returns:
            A list containing all the jobs related to the Interventor module.
        """
        
        try:
            sql_str = "select * from detectenv.job where queue ~ '^INTERVENTOR\w{1,}$';"
            jobs = []            
            
            with DatabaseWrapper() as db:
                results = db.query(sql_str)
                
            for result in results:
                job = Job(config.SCHEDULE.QUEUE[result[1]])
                job.id_job = result[0]
                job.payload = result[2]
                job.attempts = result[3]
                job.created_at = result[4]
                job.updated_at = result[5]
                
                jobs.append(job)
            
            return jobs            
        
        except:
            raise
        
    
    def get_all_interventor_failed_jobs(self) -> List[Job]:
        """Selects from Failed_Job table all the jobs regarding the Interventor module.
            
        Returns:
            A list containing all the jobs related to the Interventor module.
        """
        
        try:
            sql_str = "select * from detectenv.failed_job where queue ~ '^INTERVENTOR\w{1,}$';"
            jobs = []
            
            with DatabaseWrapper() as db:
                results = db.query(sql_str)
            
            for result in results:
                job = Job(config.SCHEDULE.QUEUE[result[2]])
                job.id_failed_job = result[0]
                job.id_job = result[1]
                job.payload = result[3]
                job.attempts = result[4]
                job.created_at = result[5]
                job.updated_at = result[6]
                job.error_message = result[7]
                
                jobs.append(job)
            
            return jobs           
        
        except:
            raise
        
    
    def get_all_interventor_jobs_based_on_queue(self, queue_type: config.SCHEDULE.QUEUE) -> List[tuple]:
        """Selects from Job table all the jobs concerning the queue named 'queue_type'.
        
        Args:
            queue_type (config.SCHEDULE.QUEUE): the name of the queue containing the jobs to be selected.
            
        Returns:
            A list containing all the jobs related to 'queue_type'.
        """
        
        try:
            sql_str = "SELECT * FROM detectenv.job WHERE queue = %s;"
            
            with DatabaseWrapper() as db:
                jobs = db.query(sql_str, (queue_type.name,))
            return jobs            
        
        except:
            raise
    
    
    def get_all_interventor_failed_jobs_based_on_queue(self, queue_type: config.SCHEDULE.QUEUE) -> List[tuple]:
        """Selects from Failed_Job table all the failed jobs concerning the queue named 'queue_type'.
        
        Args:
            queue_type (config.SCHEDULE.QUEUE): the name of the queue containing the failed jobs to be selected.
            
        Returns:
            A list containing all the failed jobs related to 'queue_type'.
        """
        
        try:
            sql_str = "SELECT * FROM detectenv.failed_job WHERE queue = %s;"
            
            with DatabaseWrapper() as db:
                failed_jobs = db.query(sql_str, (queue_type.name,))
        
            return failed_jobs
        
        except:
            raise
    
    
    def create_interventor_job(self, job: Job) -> None:
        """Persists a novel job instance in the Job table.

        Args:
            job (Job): a Job object containing all the information regarding the novel job to be persisted.
            
        Returns:
            id_job (Job): the identifier created for the new job.
        """
        try:
            sql_str = "INSERT INTO detectenv.job (queue, payload) VALUES (%s, %s) RETURNING id_job;"
                        
            with DatabaseWrapper() as db:
                db.execute(sql_str, (job.queue, job.payload,))
                id = db.fetchone()
        
            return id
        
        except:
            raise
        
        
    def create_interventor_failed_job(self, job: Job) -> tuple[int]:
        """Persists a novel job instance in the Job table.

        Args:
            job (Job): a Job object containing all the information regarding the novel job to be persisted.
            
        Returns:
            id_failed_job (Job): the identifier created for the new failed job.
        """
        try:
            sql_str = "INSERT INTO detectenv.failed_job (id_job, queue, payload, attempts, created_at, error_message) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_failed_job;"
                        
            with DatabaseWrapper() as db:
                db.execute(sql_str, (job.id_job, job.queue, job.payload, job.attempts, datetime.now(), job.error_message.args,))
                id = db.fetchone()
        
            return id
        
        except:
            raise
        
    
    def update_number_of_attempts_job(self, job: Job) -> None:
        """Increments the number of attempts of a particular job after trying to execute it without success. The field 'updated_at' is also updated with the current time when the attempt actually occurred.
        
        Args:
            job (Job): the job that is being updated.
        """
        
        try:
            sql_str = "UPDATE detectenv.job SET attempts = %s, updated_at = %s WHERE id_job = %s;"
            
            with DatabaseWrapper() as db:
                db.execute(sql_str, (job.attempts, datetime.now(), job.id_job,))
        
        except:
            raise
        
    def update_number_of_attempts_failed_job(self, failed_job: Job) -> None:
        """Increments the number of attempts of a particular failed job after trying to execute it without success. The field 'updated_at' is also updated with the current time when the attempt actually occurred.
        
        Args:
            failed_job (Job): the failed job that is being updated.
        """
        
        try:
            sql_str = "UPDATE detectenv.failed_job SET attempts = %s, updated_at = %s, error_message = %s WHERE id_job = %s;"
            
            with DatabaseWrapper() as db:
                db.execute(sql_str, (failed_job.attempts, datetime.now(), failed_job.error_message.args, failed_job.id_job,))
        
        except:
            raise
    
    
    def delete_interventor_job(self, id_job: int) -> tuple:
        """Deletes a job from the Job table and returns its information.

        Args:
            id_job (int): the id of the job to be deleted from Job table.
            
        Returns:
            a tuple containing all the attributes regarding the deleted job.
        """
        
        sql_str = "DELETE FROM detectenv.job WHERE id_job = %s RETURNING *;"
        
        try:
            with DatabaseWrapper() as db:
                db.execute(sql_str, (id_job,))
                job = db.fetchone()
                
            return job
        
        except:
            raise
        
    
    def insert_interventor_failed_job(self, failed_job: Job) -> None:
        """Creates a register in Failed_Job table, which represents a Job that has exceeded its maximum number of attempts.

        Args:
            failed_job (Job): the job object that has excceded its amount of attempts, therefore being declared as a failed job.
        """
        
        try:
            sql_str = "INSERT INTO detectenv.failed_job (id_job, queue, payload, attempts, created_at, error_message) \
                    VALUES (%s, %s, %s, %s, %s, %s);"
                    
            with DatabaseWrapper() as db:
                db.execute(sql_str, (failed_job.id, failed_job.queue, failed_job.payload, failed_job.attempts, failed_job.created_at, failed_job.error_message,))
                
        except:
            raise
        
            
    def delete_interventor_failed_job(self, id_job: int) -> tuple:
        """Deletes a job from the Failed_Job table and returns its original identifier (id_job).

        Args:
            id_failed_job (int): the id of the failed job to be deleted from Failed_Job table.
            
        Returns:
            a tuple containing the original identifier of the job deleted from Failed_Job.
        """
        
        sql_str = "DELETE FROM detectenv.failed_job WHERE id_job = %s RETURNING *;"
        
        try:
            with DatabaseWrapper() as db:
                db.execute(sql_str, (id_job,))
                job = db.fetchone()
                
            return job
        
        except:
            raise