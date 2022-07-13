import logging, pickle
from pathlib import Path
import shutil
from typing import Callable

import numpy as np
from src.config import Config as config
from src.apis.twitter import TwitterAPI
from src.fcmanager.dao import FactCheckManagerDAO
from src.utils.text_preprocessing import TextPreprocessing
from jobs.job import Job, JobManager, ExceededNumberOfAttempts, SocialMediaAlertType

# TODO: Try to make a generic 'assigning method' afterwards to be used from all modules through dependency injection.
def assign_fcamanager_jobs_to_pickle_file() -> None:
        
        dao = FactCheckManagerDAO()
        path = config.SCHEDULE.FCMANAGER_JOBS_FILE
        
        job_managers = {job.id_job: FactCheckJobManager(job, path) for job in dao.get_all_fcmanager_jobs()}
        
        try:
            with open(path, 'wb') as file:
                pickle.dump(job_managers, file)
        
        except Exception as e:
            raise Exception(f"An error occurred when trying to save the jobs in {path}:\n{e}")
            

class FactCheckingJobSocialMedia(Job):
    
    def __init__(self, schedule_type: config.SCHEDULE.QUEUE, fn_update_pickle_file: Callable[[], None] = None) -> None:
        super().__init__(schedule_type, fn_update_pickle_file)
        
        
    def create_job(self, dao, payload) -> str:
        try:
            self.payload = payload
            return str(dao.create_fcmanager_job(self)[0])
        
        except Exception as e:
            raise Exception(f"Um erro ocorreu ao persistir o job '{self.queue}' do módulo FactCheckManager: {e}")

class FactCheckJobManager(JobManager):
    
    def __init__(self, job: Job, file_path: str) -> None:
        super().__init__(job, file_path)
    

    def exceeded_number_of_max_attempts(self) -> bool:
        pass


    def manage_failed_job(self) -> None:
        pass


    def run_manager(self) -> bool:
        print(f'Executing FCManager job {self}')
    


# TODO: refactor to interface and concrete classes, one concrete for each ACF
class FactCheckManager(object):
    
    def __init__(self):
        self._twitter_api = TwitterAPI()
        self._dao = FactCheckManagerDAO()
        
        assign_fcamanager_jobs_to_pickle_file()
        
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._logger.info('FactCheckManager initialized.')
        
        
    def run(self):
        self.process_agency_feed()
    
    
    def process_agency_feed(self) -> None:
        
        if not (sheets := self._dao.has_excel_files()):
            self._logger.info('No excel files from FCAs to process.')
            return
        
        self._logger.info('Processing feed from FCAs...')
        
        # iterate over each .xlsx file within the 'received' folder.
        for sheet in sheets:
        
            dict_checked_fake_news = self._dao.process_fake_news_from_xlsx(sheet)
                        
            if dict_checked_fake_news:
                self._logger.info('Updating news that were stated as fake by the FCAs...')
                
                try:
                    self._dao.update_checked_news_in_db(dict_checked_fake_news)
                
                except IndexError as e:
                    self._logger.error(f"An error occurred during the news' updating process: {str(e)}")
                    return
                
                # TODO: emitir alerta no Twitter.
                for id_news, v in dict_checked_fake_news.items():
                    
                    if config.FCMANAGER.SOCIAL_MEDIA_ALERT_ACTIVATE:
                        
                        _, _, link = v.values()
                        
                        text_news = self._dao.get_clean_text_news_from_id(id_news).upper()
                        content   = text_news
                        fc_agency = "Boatos.org" # TODO: Hard-coded snippet. It must comprise other agencies in the future.
                        title     = f'❗ {SocialMediaAlertType.CONFIRMADO.name} COMO FAKE NEWS PELA {fc_agency.upper()}'
                        
                        with FactCheckingJobSocialMedia(config.SCHEDULE.QUEUE.FCAMANAGER_SEND_ALERT_TO_SOCIAL_MEDIA, \
                            lambda: assign_fcamanager_jobs_to_pickle_file()) as job:
                            
                            try:
                                payload = str(dict(zip(job[1].payload_keys, (title, content, link, fc_agency))))
                                id = job[1].create_job(self._dao, payload)
                                self._logger.info(f"{job[0]} {config.SCHEDULE.FCMANAGER_JOBS_FILE}: job {id} persisted successfully.")
                        
                            except Exception as e:
                                self._logger.error(e)
                    
                    self._logger.info('Registering log alert...')
                    self._dao.register_log_alert(id_news)  # log even if not published on social media network.
            else:
                self._logger.info('No news labeled as fake by the FCAs.')
                
            shutil.move(sheet, Path(Path(sheet).parent.absolute(), "processed", Path(sheet).name))
            self._logger.info(f"Excel file {sheet} has been moved to folder 'processed'.")
    
    
    # def _post_alert(self, text_news, checker, url=None):
    #     self._logger.info('Posting alert on social media...')
    #     header = 'ALERTA: a seguinte notícia foi confirmada como fakenews pela agência {}'.format(checker)

    #     # TODO: define strategy to fit tweet text according twitter limit rule of 280 characters
        
    #     text_tweet = header + '\n\n' + text_news + '\n\n' + '{}'.format(url if url else '')
    #     self._twitter_api.tweet(text_tweet)
