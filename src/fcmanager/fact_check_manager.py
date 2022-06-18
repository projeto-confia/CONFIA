import logging, pickle
from jobs.job import Job, JobManager
from src.config import Config as config
from src.apis.twitter import TwitterAPI
from src.fcmanager.dao import FactCheckManagerDAO

class FCAReceiveLabeledNewsJob(Job):
    
    def __init__(self, schedule_type: config.SCHEDULE.QUEUE) -> None:
        super().__init__(schedule_type)
        
    
    def create_job(self, dao) -> None:
        try:
            dao.create_fcmanager_job(self)
        
        except Exception as e:
            return f"Um erro ocorreu ao persistir o job '{self.queue}' do módulo Interventor: {e}"


class FCManager(JobManager):
    
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
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self._dao = FactCheckManagerDAO()
        self._twitter_api = TwitterAPI()
        self._assign_fcamanager_jobs_to_scheduler()
        self._logger.info('FactCheckManager initialized.')
        
        
    def run(self):
        self.process_agency_feed()
    
    
    def process_agency_feed(self):
        
        if not self._dao.has_excel_file():
            self._logger.info('No excel file to process.')
            return
        
        self._logger.info('Processing feed from agency...')
        checked_fakenews = self._dao.get_checked_fakenews_from_excel()
        
        if checked_fakenews:
            self._logger.info('Updating data...')
            self._dao.update_checked_news_in_db(checked_fakenews)
            for id_news, v in checked_fakenews.items():
                if config.FCMANAGER.SOCIAL_MEDIA_ALERT_ACTIVATE:
                    text_news, link = v.values()
                    self._post_alert(text_news, 'Boatos.org', link)
                self._logger.info('Registering log alert...')
                self._dao.register_log_alert(id_news)  # log even if not published on social media network
        else:
            self._logger.info('No labeled fake news.')
            
        self._logger.info('Storing excel file...')
        self._dao.store_excel_file()


    def _assign_fcamanager_jobs_to_scheduler(self) -> None:
        
        path = config.SCHEDULE.FCMANAGER_JOBS_FILE
        
        job_managers = {job.id_job: FCManager(job, path) for job in self._dao.get_all_fcmanager_jobs()}
        failed_job_managers = {job.id_job: FCManager(job, path) for job in self._dao.get_all_fcmanager_failed_jobs()}
        
        job_managers.update(failed_job_managers)
        
        try:
            with open(path, 'wb') as file:
                pickle.dump(job_managers, file)
        
        except Exception as e:
            self._logger.error(f"An error occurred when trying to save the jobs in {path}:\n{e}")
    
    
    def _post_alert(self, text_news, checker, url=None):
        self._logger.info('Posting alert on social media...')
        header = 'ALERTA: a seguinte notícia foi confirmada como fakenews pela agência {}'.format(checker)

        # TODO: define strategy to fit tweet text according twitter limit rule of 280 characters
        
        text_tweet = header + '\n\n' + text_news + '\n\n' + '{}'.format(url if url else '')
        self._twitter_api.tweet(text_tweet)
