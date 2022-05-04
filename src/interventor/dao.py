import os, shutil
from typing import List
import xlsxwriter
import pandas as pd
from src.job import Job
from datetime import datetime
from src.config import Config as config
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
                        from detectenv.news n inner join detectenv.post p on p.id_news = n.id_news \
                                            left join detectenv.checking_outcome co on co.id_news = n.id_news \
                                            left join detectenv.curatorship cur on cur.id_news = n.id_news \
                        where n.datetime_publication > current_date - interval '" + str(window_size) + "' day \
                            and n.ground_truth_label is null \
                            and n.classification_outcome = True \
                            and co.id_news is null \
                            and cur.id_news is null \
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
        
        
    def persist_candidates_to_check(self, candidates_id, id_trusted_agency):
        sql_string = "INSERT INTO detectenv.checking_outcome \
                        (id_news, id_trusted_agency) \
                        VALUES (%s,%s);"
        try:
            with DatabaseWrapper() as db:
                for id_news in candidates_id:
                    db.execute(sql_string, (id_news, id_trusted_agency))
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
                
            return db.fetchone()
        
        except:
            raise
        
    
    def update_number_of_attempts(self, id: int, num_attempts: int, job_table: bool) -> None:
        """Increments the number of attempts of a particular job after trying to execute it without success. The field 'updated_at' is also updated with the current time when the attempt actually occurred.
        
        Args:
            id (int): the id of the job to get its number of attempts updated.
            num_attempts (int): an updated number that represents the failed attempts to execute this job.
            job_table (bool): if 'True' the register of Job table is updated; if 'False', updates the register of Failed_Job table instead.
        """
        
        try:
            sql_str = "UPDATE detectenv.job SET attempts = %s, updated_at = %s WHERE id_job = %s;" if job_table else "UPDATE detectenv.failed_job SET attempts = %s, updated_at = %s WHERE id_failed_job = %s;"
            
            with DatabaseWrapper() as db:
                db.execute(sql_str, (id, num_attempts, datetime.now(),))
        
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
                return db.fetchone()
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
        
            
    def delete_interventor_failed_job(self, id_failed_job: int) -> tuple:
        """Deletes a job from the Failed_Job table and returns its original identifier (id_job).

        Args:
            id_failed_job (int): the id of the failed job to be deleted from Failed_Job table.
            
        Returns:
            a tuple containing the original identifier of the job deleted from Failed_Job.
        """
        
        sql_str = "DELETE FROM detectenv.failed_job WHERE id_failed_job = %s RETURNING id_failed_job;"
        
        try:
            with DatabaseWrapper() as db:
                db.execute(sql_str, (id_failed_job,))
                return db.fetchone()
        except:
            raise