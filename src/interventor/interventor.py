from enum import Enum, auto
from typing import Callable
from jobs.job import Job, JobManager
from src.utils.email import EmailAPI
from src.config import Config as config
from src.apis.twitter import TwitterAPI
from psycopg2.errors import UniqueViolation
from src.interventor.dao import InterventorDAO
from src.utils.text_preprocessing import TextPreprocessing
import ast, logging, pickle, src.interventor.endpoints as endpoints

#! TAREFAS A SEREM CONCLUÍDAS
# def run(self):
#     # Executar queue de envios para ACF
#     # Executar queue de alertas na rede social

class SocialMediaAlertType(Enum):
    DETECTADO = auto()
    CONFIRMADO = auto()
    SIMILARIDADE = auto()
    

def assign_interventor_jobs_to_pickle_file() -> None:
    """Helper function for keeping the Interventor module's pickle file up-to-date after insertions and deletions in the Job table."""
    
    path = config.SCHEDULE.INTERVENTOR_JOBS_FILE
    dao = InterventorDAO()
    
    job_managers = {job.id_job: InterventorManager(job, path) for job in dao.get_all_interventor_jobs()}
    
    try:
        with open(path, 'wb') as file:
            pickle.dump(job_managers, file)
    
    except Exception as e:
        raise Exception(f"An error occurred when trying to save the jobs in {path}:\n{e}")
    


class InterventorJobFCA(Job):
    
    def __init__(self, schedule_type: config.SCHEDULE.QUEUE, fn_update_pickle_file: Callable[[], None] = None) -> None:
        super().__init__(schedule_type, fn_update_pickle_file)
        
    
    def create_job(self, dao, payload) -> str:
        try:
            self.payload = payload
            return str(dao.create_interventor_job(self)[0])
        
        except Exception as e:
            return f"An error has occurred when persisting the job '{self.queue}' from Interventor's module: {e}"
        
        

class InterventorJobSocialMedia(Job):
    
    def __init__(self, schedule_type: config.SCHEDULE.QUEUE, fn_update_pickle_file: Callable[[], None] = None) -> None:
        super().__init__(schedule_type, fn_update_pickle_file)
        
    
    def create_job(self, dao, payload) -> str:
        try:
            self.payload = payload
            return str(dao.create_interventor_job(self)[0])
        
        except Exception as e:
            return f"An error has occurred when persisting the job '{self.queue}' from Interventor's module: {e}"
        


class InterventorManager(JobManager):
    
    def __init__(self, job: Job, file_path: str) -> None:
        super().__init__(job, file_path)
        self._twitter_api = TwitterAPI()
        self.dao = InterventorDAO()

    
    def check_number_of_max_attempts(self, count: bool = True) -> bool:
        
        if count:
            self.job.__dict__["attempts"] += 1
            
        current_attempts = self.job.__dict__["attempts"]
        max_attempts = self.job.__dict__["max_attempts"]
        
        return True if current_attempts > max_attempts else False
            

    def manage_failed_job(self) -> str:
        
        has_exceeded = self.check_number_of_max_attempts()
        attempts = self.job.__dict__["attempts"]
        max_attempts = self.job.__dict__["max_attempts"]
        
        if not has_exceeded:
            self.dao.update_number_of_attempts_job(self.job)
            message = f"Interventor's job Nº {self.get_id_job} has failed. A novel execution attempt was already scheduled ({attempts}/{max_attempts})."
            
        else:
            first_time: bool = False
            try:
                _ = self.dao.get_failed_interventor_job(self.get_id_job)
            
            except IndexError:
                id_failed_job = self.dao.create_interventor_failed_job(self.job)
                first_time = True
            
            if not first_time:
                self.dao.update_number_of_attempts_failed_job(self.job)
                message = f"Interventor's failed job Nº {self.get_id_job} has failed. A novel execution attempt was already scheduled."
            
            else:
                message = f"Interventor's job Nº {self.get_id_job} maxed out the number of attempts and it was moved to the Failed Jobs table with id {id_failed_job[0]}."
                self.dao.delete_interventor_job(self.get_id_job)

        assign_interventor_jobs_to_pickle_file()
        
        return message

    async def run_manager(self) -> str:
        
        if config.SCHEDULE.QUEUE[self.job.queue] == config.SCHEDULE.QUEUE.INTERVENTOR_SEND_ALERT_TO_SOCIAL_MEDIA:
            
            if not config.INTERVENTOR.SOCIAL_MEDIA_ALERT_ACTIVATE:
                return "AUTOMATA is set to do not send alerts to social media."
            
            try:
                if not self.check_number_of_max_attempts(False):
                    deleted_job = self.dao.get_interventor_job(self.get_id_job)
                    payload = payload = ast.literal_eval(deleted_job[2])
                
                else:
                    deleted_job = self.dao.get_failed_interventor_job(self.get_id_job)
                    payload = payload = ast.literal_eval(deleted_job[3])
                
                title = payload["title"]
                content = payload["content"]
                
                request_payload = await endpoints.post_new_fake_news_in_confia_portal(payload)
                slug  = await endpoints.update_fake_news_in_confia_portal(request_payload.text)
                
                tweet = TextPreprocessing.prepare_tweet_for_posting(title, content, slug)
                message = self._twitter_api.tweet(tweet)
                
                if not self.check_number_of_max_attempts(False):
                    deleted_job = self.dao.delete_interventor_job(self.get_id_job)
                    message = f"Job {deleted_job[1]} Nº {self.get_id_job} has been executed successfully: {message}\n\n"
                else:
                    message = f"Job {deleted_job[2]} Nº {self.get_id_job} has been executed successfully: {message}\n\n"
                    deleted_job = self.dao.delete_interventor_failed_job(self.get_id_job)
                    
                assign_interventor_jobs_to_pickle_file()
                return message
            
            except endpoints.InvalidResponseError as e:
                self.job.error_message = e
                raise Exception(e)
            
            except Exception as e:
                error = f"An error occurred when trying to delete job Nº {self.get_id_job} from database: {e}"
                self.job.error_message = error
                raise Exception(error)
            
        
        elif config.SCHEDULE.QUEUE[self.job.queue] == config.SCHEDULE.QUEUE.INTERVENTOR_SEND_NEWS_TO_FCA:
            print(f"{config.SCHEDULE.QUEUE.INTERVENTOR_SEND_NEWS_TO_FCA.name} ")
            quit()


# TODO: refactor to interface and concrete classes, one concrete for each FCA
class Interventor(object):
    
    def __init__(self):
        
        self._email_api = EmailAPI()
        self._dao = InterventorDAO()
        self._twitter_api = TwitterAPI()
        self._text_preprocessor = TextPreprocessing()
        
        self._all_fca_news = self._get_all_agency_news()
        self._logger = logging.getLogger(config.LOGGING.NAME)
        
        # assigns each Interventor job to a job manager and subscribes it into the scheduler.
        assign_interventor_jobs_to_pickle_file()
        self._logger.info("Interventor initialized.")
        
        
    def run(self):
        self._process_news()
        self._process_curatorship()
        

    def _get_all_agency_news(self):
        all_fca_news = self._dao.get_all_agency_news()
        
        for i, (_, publication_title, _) in enumerate(all_fca_news):
            all_fca_news[i] += (self._text_preprocessor.text_cleaning(publication_title),)
            
        return all_fca_news
        
        
    def _process_news(self):
        self._logger.info('Selecting news to be verified...')
        candidates = self._dao.select_news_to_be_verified(window_size=config.INTERVENTOR.WINDOW_SIZE,
                                                          prob_classif_threshold=config.INTERVENTOR.PROB_CLASSIF_THRESHOLD,
                                                          num_records=config.INTERVENTOR.NUM_NEWS_TO_SELECT)
        if not candidates:
            self._logger.info('No news to be verified.')
            return
        
        if config.INTERVENTOR.CURATOR:
            self._persist_news_to_curatorship(candidates)
            return
        
        self._persist_news(candidates)
                
                
    def _persist_news_to_curatorship(self, news):
        self._logger.info('Persisting news to curatorship...')
        similars, candidates_to_check = self._split_similar_news(news)
        candidates_to_check = [c + (None,) for c in candidates_to_check]
        self._dao.persist_to_curatorship(similars + candidates_to_check)
        
        
    def _split_similar_news(self, news):
        """Split news list in two: list of similars and list of not similars
        
        Identify records on news list that is similar to early published by FCA.
        Add FCA id news to those identified as similar.

        Args:
            news (list): list of news
        
        Returns:
            tuple: (list of similars, list of not similars)
        """
        #! VERIFICAR ESSE CÓDIGO.
        
        similars, not_similars = list(), list()
        for i, (_, text_news) in enumerate(news):
            text_news_cleaned = self._text_preprocessor.text_cleaning(text_news)
        
            for id_news_checked, _, _, publication_title_cleaned in self._all_fca_news:
                is_similar, _ = self._text_preprocessor.check_duplications(text_news_cleaned, publication_title_cleaned)
        
                if is_similar:
                    similars.append(news[i] + (id_news_checked,))
                    break
            else:
                not_similars.append(news[i])
        
        return (similars, not_similars)
    
    
    def _persist_news(self, news):
        """Process and persist selected classified fake news
        
        News must be a list of tuples like (id_news, text_news)

        Args:
            news (list): list of tuples like (id_news, text_news)
        """
        
        self._logger.info('Processing news...')
        similars, candidates_to_check = self._split_similar_news(news)
        self._process_similars(similars)
        self._process_candidates_to_check(candidates_to_check)
        
    
    #! TESTAR ESSE CÓDIGO.
    def _process_similars(self, similars):
        self._logger.info('Processing similar news...')
        self._dao.persist_similar_news(similars)
        
        for similar_news in similars:
            
            with InterventorJobSocialMedia(config.SCHEDULE.QUEUE.INTERVENTOR_SEND_ALERT_TO_SOCIAL_MEDIA, \
                lambda: assign_interventor_jobs_to_pickle_file()) as job:
                
                try:
                    text_news_cleaned = self._dao.get_clean_text_news_from_id(similar_news)
                    title = text_news_cleaned.upper() if len(text_news_cleaned) < 6 else " ".join(text_news_cleaned.split()[:6]).upper()
                    
                    payload = str(dict(zip(job[1].payload_keys, \
                        (f"⚠️ ALERTA de {SocialMediaAlertType.SIMILARIDADE.name} - {title}", TextPreprocessing.slugify(title.lower()), text_news_cleaned))))
                    
                    id = job[1].create_job(self._dao, payload)
                    self._logger.info(f"{job[0]} {config.SCHEDULE.INTERVENTOR_JOBS_FILE}: job {id} persisted successfully.")            
            
                except Exception as e:
                    self._logger.error(e)
    
    
    #! TESTAR ESSE CÓDIGO.
    def _process_candidates_to_check(self, candidates_to_check):
        self._logger.info('Processing news to be checked...')
        
        if config.INTERVENTOR.CURATOR:
            curated = [c for c in candidates_to_check if c[3] != None]
            candidates_to_check = [c for c in candidates_to_check if c[3] == None]
        
            if curated:
                self._process_labeled_curatorship(curated)
        
            if not candidates_to_check:
                return
        
        candidates_id = [c[0] for c in candidates_to_check]
        id_trusted_agency,_,_,_ = self._dao.get_data_from_agency('Boatos.org')
        
        for id_news in candidates_id:
            
            try:
                self._dao.persist_candidates_to_check(id_news, id_trusted_agency)
            
            except UniqueViolation as e:
                error = e.args[0].replace('\n', ' ')
                self._logger.error(f"News with id {id_news} and FCA's id {id_trusted_agency} already exists in table 'detectenv.checking_outcome', thus violating the unique constraint pair: {error}")
        
        
        message = InterventorDAO.build_excel_sheet(candidates_to_check)
        self._logger.info(message)
        
        quit()

        # for candidate_news in candidates_to_check:
        #     ...
        
        #! CRIAR ROTINA PARA ENVIO DA PLANILHA POR EMAIL.
        
        with InterventorJobFCA(config.SCHEDULE.QUEUE.INTERVENTOR_SEND_NEWS_TO_FCA, \
            assign_interventor_jobs_to_pickle_file) as job:
            
            
            for fca in config.INTERVENTOR.FACT_CHECK_AGENCIES:
                
                fca_info = self._dao.get_data_from_agency('Boatos.org')
                fca_email = fca_info[1]
                
                email = EmailAPI()
        
            
            # self._social_media_job.create_job(self._dao, dict(zip(self._social_media_job.payload_keys, (candidate_news, SocialMediaAlertType.DETECTADO.name))))
            
            # self._fca_job.create_job(
            #     self._dao, **dict(zip(self._social_media_job.payload_keys, (candidate_news, SocialMediaAlertType.DETECTADO.name))))
        
        # TODO: implement functions        
        # file_id = self._build_excel(candidates_to_check)
        # self._create_send_job(file_id)
        # self._create_alert_job(candidates_to_check, alert_type='detected')
        
        
        
    def _process_labeled_curatorship(self, curated):
        
        news = [(c[0], c[3]) for c in curated]
        self._dao.update_ground_truth_label(news)
        # TODO: implement function
        fake_news = [c[0] for c in curated if c[3]]
        
        for news in fake_news:
            
            with InterventorJobSocialMedia(config.SCHEDULE.QUEUE.INTERVENTOR_SEND_ALERT_TO_SOCIAL_MEDIA, \
                lambda: assign_interventor_jobs_to_pickle_file()) as job:
                
                try:
                    text_news_cleaned = self._dao.get_clean_text_news_from_id(news)
                    title = text_news_cleaned.upper() if len(text_news_cleaned) < 6 else " ".join(text_news_cleaned.split()[:6]).upper()
                    payload = str(dict(zip(job[1].payload_keys, \
                        (f"❗ {SocialMediaAlertType.CONFIRMADO.name} COMO FAKE NEWS - {title}", TextPreprocessing.slugify(title.lower()), text_news_cleaned))))
                    
                    id = job[1].create_job(self._dao, payload)
                    self._logger.info(f"{job[0]} {config.SCHEDULE.INTERVENTOR_JOBS_FILE}: job {id} persisted successfully.")            
            
                except Exception as e:
                    self._logger.error(e)
    
    
    def _create_alert_job(self, news, alert_type):
        """Add alerts in social media tasks into jobs queue

        Args:
            news (list): list of news
            alert_type (str): {'similar', 'detected', 'labeled'} type of alert.
        """
        
        assert alert_type in ('similar', 'detected', 'labeled')
        # TODO: build specific module in utils package to register jobs
        pass
    
    
    def _create_send_job(self, file_id):
        pass
    
    
    def _process_curatorship(self):
        while (curations := self._dao.get_curations()):
            self._logger.info('Processing curated news...')
            curations_id = [curation[5] for curation in curations]
            similars = [curation[:3] for curation in curations if curation[4]]
            candidates_to_check = [curation[:4] for curation in curations if not curation[4]]
            
            if similars:
                self._process_similars(similars)
                
            if candidates_to_check:
                self._process_candidates_to_check(candidates_to_check)
                
            self._dao.close_curations(tuple(curations_id))
        
        else:
            self._logger.info('No more curations to process.')
