import ast
import shutil
import logging, pickle
from pathlib import Path
from typing import Callable
from jobs import dao as dao_jobs
from src.config import Config as config
from src.apis.twitter import TwitterAPI
from src.fcmanager.dao import FactCheckManagerDAO
from src.utils.text_preprocessing import TextPreprocessing
from jobs.job import Job, JobManager, ExceededNumberOfAttempts, SocialMediaAlertType

# TODO: Try to make a generic 'assigning method' afterwards to be used from all modules through dependency injection.
def assign_fcamanager_jobs_to_pickle_file() -> None:
        
        path = config.SCHEDULE.FCMANAGER_JOBS_FILE
        
        job_managers = {job.id_job: FactCheckJobManager(job, path) for job in dao_jobs.get_all_fcmanager_jobs()}
        
        try:
            with open(path, 'wb') as file:
                pickle.dump(job_managers, file)
        
        except Exception as e:
            raise Exception(f"An error occurred when trying to save the jobs in {path}:\n{e}")
            

class FactCheckingJobSocialMedia(Job):
    
    def __init__(self, schedule_type: config.SCHEDULE.QUEUE, fn_update_pickle_file: Callable[[], None] = None) -> None:
        super().__init__(schedule_type, fn_update_pickle_file)
        
        
    def create_job(self, payload) -> str:
        try:
            self.payload = payload
            return str(dao_jobs.create_job(self)[0])
        
        except Exception as e:
            raise Exception(f"Um erro ocorreu ao persistir o job '{self.queue}' do módulo FactCheckManager: {e}")

class FactCheckJobManager(JobManager):
    
    def __init__(self, job: Job, file_path: str) -> None:
        super().__init__(job, file_path)
        self.dao = FactCheckManagerDAO()
        self._twitter_api = TwitterAPI()


    def manage_failed_job(self) -> None:
        
        has_exceeded = self.exceeded_number_of_max_attempts()
        message = ""
        
        if not has_exceeded:
            dao_jobs.update_number_of_attempts_job(self.job)
            
        else:
            id_failed_job = dao_jobs.create_failed_job(self.job)
            message = f"FactCheckManager's job Nº {self.get_id_job} maxed out the number of attempts and it was moved to table 'failed_jobs' with id {id_failed_job[0]}."
            dao_jobs.delete_job(self.get_id_job)

        assign_fcamanager_jobs_to_pickle_file()
        return message


    async def run_manager(self) -> str:
        return await self._fca_send_alert_to_social_media()
        
        
    async def _fca_send_alert_to_social_media(self) -> str:
        
        """Auxiliary function to send alerts to social media.

        Raises:
            ExceededNumberOfAttempts: when the number of attempts of the job has been exceeded.
            Exception: when an error occurred when trying to delete the job from the database.

        Returns:
            str: a message with the result of the execution of the job.
        """
        
        if not config.FCMANAGER.SOCIAL_MEDIA_ALERT_ACTIVATE:
            return "AUTOMATA is set to do not send alerts to social media."
            
        try:
            if not self.exceeded_number_of_max_attempts(False):
                deleted_job = dao_jobs.get_job(self.get_id_job)
                payload = payload = ast.literal_eval(deleted_job[2])
            else:
                raise ExceededNumberOfAttempts(f"The number of attempts of job {self.job.id_job} has been exceeded.")
            
            title = payload["title"]
            content = payload["content"]
            link = payload["link"]
            
            tweet = TextPreprocessing.prepare_tweet_for_posting(title, content, link)
            message = self._twitter_api.tweet(tweet)
            
            deleted_job = dao_jobs.delete_job(self.get_id_job)
            message = f"Job {deleted_job[1]} Nº {self.get_id_job} has been executed successfully: {message}"
                
            assign_fcamanager_jobs_to_pickle_file()
            return message
        
        except ExceededNumberOfAttempts as e:
            self.job.error_message = e
            raise Exception(e)
        
        except Exception as e:
            error = f"An error occurred when trying to delete job Nº {self.get_id_job} from database: {e}"
            self.job.error_message = error
            raise Exception(error)
    

# TODO: refactor to interface and concrete classes, one concrete for each ACF
class FactCheckManager(object):
    
    def __init__(self):
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
                
                for id_news, v in dict_checked_fake_news.items():
                                            
                    _, _, link = v.values()
                    
                    content   = self._dao.get_clean_text_news_from_id(id_news).upper()
                    fc_agency = "Boatos.org" # TODO: Hard-coded snippet. It must comprise other agencies in the future.
                    title     = f'❗ {SocialMediaAlertType.CONFIRMADO.name} COMO FAKE NEWS PELA {fc_agency.upper()}'
                    
                    with FactCheckingJobSocialMedia(config.SCHEDULE.QUEUE.FCAMANAGER_SEND_ALERT_TO_SOCIAL_MEDIA, \
                        lambda: assign_fcamanager_jobs_to_pickle_file()) as job:
                        
                        try:
                            payload = str(dict(zip(job[1].payload_keys, (title, content, link, fc_agency))))
                            id = job[1].create_job(payload)
                            self._logger.info(f"{job[0]} {config.SCHEDULE.FCMANAGER_JOBS_FILE}: job {id} persisted successfully.")
                    
                        except Exception as e:
                            self._logger.error(e)
                    
                    self._logger.info('Registering log alert...')
                    self._dao.register_log_alert(id_news)  # log even if not published on social media network.
            else:
                self._logger.info('No news labeled as fake by the FCAs.')
                
            shutil.move(sheet, Path(Path(sheet).parent.absolute(), "processed", Path(sheet).name))
            self._logger.info(f"Excel file {sheet} has been moved to folder 'processed'.")