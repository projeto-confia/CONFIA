import os, shutil
import pandas as pd
from typing import List
from jobs.job import Job
from datetime import datetime
from src.config import Config as config
from src.orm.db_wrapper import DatabaseWrapper


class FactCheckManagerDAO(object):
    
    def __init__(self):
        self.excel_filepath_received = os.path.join('src', 'data', 'acf', 'received', 'confia.xlsx')
        self._excel_filepath_processed = os.path.join('src', 'data', 'acf', 'received', 'processed')
        
    
    def get_all_fcmanager_jobs(self) -> List[Job]:
        """Selects from Job table all the jobs regarding the FCAManager module.
            
        Returns:
            A list containing all the jobs related to the FCAManager module.
        """
        
        try:
            sql_str = "select * from detectenv.job where queue ~ '^FCAMANAGER\w{1,}$';"
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
        
        
    def get_all_fcmanager_failed_jobs(self) -> List[Job]:
        """Selects from Failed_Job table all the jobs regarding the FCAManager module.
            
        Returns:
            A list containing all the jobs related to the FCAManager module.
        """
    
        try:
            sql_str = "select * from detectenv.failed_job where queue ~ '^FCAMANAGER\w{1,}$';"
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

    
    def create_fcmanager_job(self, job: Job):
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
    
    
    def has_excel_file(self):
        return os.path.exists(self.excel_filepath_received)
    
    
    def get_checked_fakenews_from_excel(self):
        # load excel file content with pandas
        df = pd.read_excel(self.excel_filepath_received, 
                           dtype={'Id': int, 'Texto': str, 'Checagem': str, 'Link': str},
                           na_filter = False)
        
        # remove accidental blank spaces
        df['Checagem'] = df['Checagem'].apply(str.strip)
        df['Link'] = df['Link'].apply(str.strip)
        
        # filter only checked records
        df = df[df['Checagem'].notnull()]
        
        # assure value "fake"
        df['Checagem'] = df['Checagem'].str.lower()
        
        # filter only fake records, drop column 'Checagem'
        df = df[df['Checagem'] == 'fake']
        df.drop(columns=['Checagem'], inplace=True)
        
        # return dict
        df.set_index('Id', inplace=True)
        return df.to_dict(orient='index')
    
    
    def update_checked_news_in_db(self, checked_fakenews):

        # TODO: if some id record doesn't exist in the database table, register occurrence in the log
        
        try:
            dt = datetime.now()
            fakenews_ids = tuple(checked_fakenews.keys())
            
            # TODO: adds id_trusted_agency in WHERE clause
            sql_string_1 = "UPDATE detectenv.checking_outcome \
                            SET datetime_outcome = %s, \
                            is_fake = %s, \
                            trusted_agency_link = %s \
                            WHERE id_news = %s;"

            # TODO: in the future, add rule to decide between outcomes from many agencies
            sql_string_2 = "UPDATE detectenv.news \
                            SET ground_truth_label = true \
                            WHERE id_news IN %s;"
                            
            with DatabaseWrapper() as db:
                for id_news, v in checked_fakenews.items():
                    _, link = v.values()
                    args = (dt, True, link, id_news)
                    db.execute(sql_string_1, args)
                    
                db.execute(sql_string_2, (fakenews_ids,))
        except:
            raise
        
        
    def store_excel_file(self):
        shutil.move(self.excel_filepath_received, os.path.join(self._excel_filepath_processed, '{}.xlsx'.format(datetime.now())))
        
        
    def register_log_alert(self, id_news):
        try:
            dt = datetime.now()
            sql_string = "INSERT INTO detectenv.action_log \
                        (id_action, id_news, datetime_log, description_log) \
                        VALUES ((SELECT act.id_action \
                                FROM detectenv.action_type act \
                                WHERE upper(act.name_action) = upper('alert_checked')), \
                                %s, %s, 'alerta registrado no twitter');"
                                
            with DatabaseWrapper() as db:
                db.execute(sql_string, (id_news, dt))
        except:
            raise
