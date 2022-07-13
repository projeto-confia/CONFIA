from enum import Enum, auto
from typing import Callable
from src.utils.email import EmailAPI
from src.config import Config as config
from src.apis.twitter import TwitterAPI
from psycopg2.errors import UniqueViolation
from smtplib import SMTPAuthenticationError
from src.interventor.dao import InterventorDAO
from src.utils.text_preprocessing import TextPreprocessing
import ast, logging, pickle, shutil, src.interventor.endpoints as endpoints
from jobs.job import Job, JobManager, ExceededNumberOfAttempts, SocialMediaAlertType
        

def assign_interventor_jobs_to_pickle_file() -> None:
    """Helper function for keeping the Interventor module's pickle file up-to-date after insertions and deletions in the Job table."""
    
    dao = InterventorDAO()
    path = config.SCHEDULE.INTERVENTOR_JOBS_FILE
    
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

    
    def exceeded_number_of_max_attempts(self, count: bool = True) -> bool:
        
        if count:
            self.job.__dict__["attempts"] += 1
            
        current_attempts = self.job.__dict__["attempts"]
        max_attempts = self.job.__dict__["max_attempts"]
        
        return True if current_attempts > max_attempts else False
            

    def manage_failed_job(self) -> str:
        
        has_exceeded = self.exceeded_number_of_max_attempts()
        attempts = self.job.__dict__["attempts"]
        max_attempts = self.job.__dict__["max_attempts"]
        
        if not has_exceeded:
            self.dao.update_number_of_attempts_job(self.job)
            message = f"Interventor's job {self.get_id_job} has failed. A novel execution attempt was already scheduled ({attempts}/{max_attempts})."
            
        else:
            id_failed_job = self.dao.create_interventor_failed_job(self.job)
    
            message = f"Interventor's job Nº {self.get_id_job} maxed out the number of attempts and it was moved to the Failed Jobs table with id {id_failed_job[0]}."
    
            self.dao.delete_interventor_job(self.get_id_job)

        assign_interventor_jobs_to_pickle_file()
        return message
    

    async def run_manager(self) -> str:
        
        if config.SCHEDULE.QUEUE[self.job.queue] == config.SCHEDULE.QUEUE.INTERVENTOR_SEND_ALERT_TO_SOCIAL_MEDIA:
            
            return await self._send_alerts_to_social_media()
        
        elif config.SCHEDULE.QUEUE[self.job.queue] == config.SCHEDULE.QUEUE.INTERVENTOR_SEND_NEWS_TO_FCA:
            
            return await self._send_email_to_fca()
        
        
    async def _send_email_to_fca(self) -> str:
        
        """Auxiliary function to send an email to the FCA if the CURATORSHIP flag is set to False.

        Raises:
            ExceededNumberOfAttempts: when the number of attempts of the job has been exceeded.
            SMTPAuthenticationError: when occurred an error when trying to authenticate with the SMTP server.
            Exception: when an error occurred when trying to delete the job from the database.

        Returns:
            str: a message with the result of the execution of the job.
        """
            
        try:
            if not self.exceeded_number_of_max_attempts(False):
                deleted_job = self.dao.get_interventor_job(self.get_id_job)
                payload = payload = ast.literal_eval(deleted_job[2])
            else:
                raise ExceededNumberOfAttempts(f"The number of attempts of job {self.job.id_job} has been exceeded.")
            
            payload = ast.literal_eval(self.job.__dict__["payload"])
            
            number_of_news_to_send = payload["number_of_news_to_send"]
            fca_email_address = payload["fca_email_address"]
            xlsx_path = payload["xlsx_path"]
            
            id_agency, name_agency = self.dao.get_id_and_name_of_trusted_agency_by_its_email_address(fca_email_address)
            
            subject = f"Remessa de {number_of_news_to_send} Possíveis Fake News" if number_of_news_to_send > 1 \
                else f"Remessa de {number_of_news_to_send} Possível Fake News"
            
            body = f"Prezados colaboradores da {name_agency},\n\nsegue em anexo uma planilha contendo {number_of_news_to_send} notícias consideradas pelo AUTOMATA como possíveis fake news. Solicitamos, por gentileza, que averiguem a veracidade das respectivas notícias contidas nessa planilha, e que a retorne assim que possível com os campos em branco devidamente preenchidos.\n\nDesde já, agradecemos pela cooperação.\n\nAtenciosamente,\nEquipe CONFIA." if number_of_news_to_send > 1 \
                else f"Prezados colaboradores da {name_agency},\n\nsegue em anexo uma planilha contendo {number_of_news_to_send} notícia considerada pelo AUTOMATA como uma possível fake news. Solicitamos, por gentileza, que averiguem a veracidade da respectiva notícia contida nessa planilha, e que a retorne assim que possível com os campos em branco devidamente preenchidos.\n\nDesde já, agradecemos pela cooperação.\n\nAtenciosamente,\nEquipe CONFIA."
            
            email_manager = EmailAPI()
            
            email_manager.send(to_whom=[fca_email_address], text_subject=subject, text_message=body, attachment_list=[xlsx_path])
            
            deleted_job = self.dao.delete_interventor_job(self.get_id_job)
            send_message = ""            
            
            for id_news in self.dao.get_all_distinct_id_news_from_checking_outcome():
                self.dao.update_the_time_when_the_news_was_sent_to_fca(id_news[0], id_agency)
            
            assign_interventor_jobs_to_pickle_file()
            
            # move a planilha da pasta 'to_send' para a pasta 'sent' se não houver mais jobs de envio de emails para as ACFs.
            if not self.dao.check_whether_there_are_fca_email_jobs_in_pkl():
                shutil.move(xlsx_path, config.INTERVENTOR.PATH_NEWS_SENT_AS_EXCEL_SHEET_TO_FCAs)
                send_message = f"\nSpreadsheet {xlsx_path} has been moved to the folder 'sent' for documentation purposes."
                message = f"Email referred to job {deleted_job[1]} Nº {self.get_id_job} has been sent successfully.{send_message}"
            
            else:
                message = f"Email referred to job {deleted_job[1]} Nº {self.get_id_job} has been sent successfully."
                
            return message
    
        except (SMTPAuthenticationError, ExceededNumberOfAttempts) as e:
            self.job.error_message = e
            raise Exception(e)
        
        except Exception as e:
            error = f"An error occurred when trying to delete job Nº {self.get_id_job} from database: {e}"
            self.job.error_message = error
            raise Exception(error)
        
        
    async def _send_alerts_to_social_media(self) -> str:
        
        """Auxiliary function to send alerts to social media.

        Raises:
            ExceededNumberOfAttempts: when the number of attempts of the job has been exceeded.
            endpoint.InvalidResponseError: when the response from the endpoint is invalid (500).
            Exception: when an error occurred when trying to delete the job from the database.

        Returns:
            str: a message with the result of the execution of the job.
        """
        
        if not config.INTERVENTOR.SOCIAL_MEDIA_ALERT_ACTIVATE:
            return "AUTOMATA is set to do not send alerts to social media."
            
        try:
            if not self.exceeded_number_of_max_attempts(False):
                deleted_job = self.dao.get_interventor_job(self.get_id_job)
                payload = payload = ast.literal_eval(deleted_job[2])
            else:
                raise ExceededNumberOfAttempts(f"The number of attempts of job {self.job.id_job} has been exceeded.")
            
            title = payload["title"]
            content = payload["content"]
            slug = payload["slug"]
            
            if slug:
                request_payload = await endpoints.post_new_fake_news_in_confia_portal(payload)
                slug  = await endpoints.update_fake_news_in_confia_portal(request_payload.text)
            
            tweet = TextPreprocessing.prepare_tweet_for_posting(title, content, slug)
            message = self._twitter_api.tweet(tweet)
            
            deleted_job = self.dao.delete_interventor_job(self.get_id_job)
            message = f"Job {deleted_job[1]} Nº {self.get_id_job} has been executed successfully: {message}"
                
            assign_interventor_jobs_to_pickle_file()
            return message
        
        except (endpoints.InvalidResponseError, ExceededNumberOfAttempts) as e:
            self.job.error_message = e
            raise Exception(e)
        
        except Exception as e:
            error = f"An error occurred when trying to delete job Nº {self.get_id_job} from database: {e}"
            self.job.error_message = error
            raise Exception(error)


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
        
        
    #! MÉTODO PRINCIPAL DO INTERVENTOR.
    def run(self):
        
        self._process_news()
        self._process_curatorship()
        

    #! PRIMEIRO MÉTODO A SER EXECUTADO NO MÉTODO RUN().
    def _process_news(self):
        
        self._logger.info('Selecting news to be verified...')
        candidates = self._dao.select_news_to_be_verified(window_size=config.INTERVENTOR.WINDOW_SIZE,
                                                          prob_classif_threshold=config.INTERVENTOR.PROB_CLASSIF_THRESHOLD,
                                                          num_records=config.INTERVENTOR.NUM_NEWS_TO_SELECT)
        
        classified_as_fake     = [candidate for candidate in candidates if candidate[2] == True]
        classified_as_not_fake = [candidate for candidate in candidates if candidate[2] == False]
        
        if classified_as_not_fake:
            self._logger.info("Checking the existence of similar news identified as 'fake' by FCAs but classified as 'not fake' by AUTOMATA.")
            self._persist_news(classified_as_not_fake)           
        
        if not classified_as_fake:
            self._logger.info('No news to be verified.')
            return
        
        if config.INTERVENTOR.CURATORSHIP:
            self._persist_news_to_curatorship(classified_as_fake)
            return
        
        self._persist_news(classified_as_fake)
        
    
    #! SEGUNDO MÉTODO A SER EXECUTADO NO MÉTODO RUN().
    def _process_curatorship(self):
        
        while (curations := self._dao.get_curations()):
            
            self._logger.info('Processing curated news...')
            curations_id = [curation[5] for curation in curations]
            similars = [curation[:3] for curation in curations if curation[4]]
            candidates_to_check = [curation[:4] for curation in curations if not curation[4]]
            
            if similars:
                similars = [similar[:1] + (None,) + similar[1:] for similar in similars]
                self._process_similars(similars)
                
            if candidates_to_check:
                self._process_candidates_to_check(candidates_to_check)
                
            self._dao.close_curations(tuple(curations_id))
        
        else:
            self._logger.info('No more curations to process.')
    
    
    def _persist_news_to_curatorship(self, news):
        
        self._logger.info('Persisting news to curatorship...')
        similars, candidates_to_check = self._split_similar_news(news)
        candidates_to_check = [c + (None,) for c in candidates_to_check]
        
        for id_news, _, _, id_news_checked in similars + candidates_to_check:
        
            try: # só pode haver um 'id_news' único na tabela 'curatorship'.
                self._dao.persist_to_curatorship(id_news, id_news_checked)
                
            except UniqueViolation as e:
                error = e.args[0].replace('\n', ' ')
                self._logger.error(f"An error occurred when trying to persist novel news to curatorship: {error}")
        

    def _persist_news(self, news):
        """Process and persist the selected news classified as fake.
        
        News must be a list of tuples like (id_news, text_news)

        Args:
            news (list): list of tuples like (id_news, text_news)
        """
        
        self._logger.info('Processing news...')
        similars, candidates_to_check = self._split_similar_news(news)
        
        self._process_similars(similars)
        
        if candidates_to_check and len(candidates_to_check) == 4:
            self._process_candidates_to_check(candidates_to_check)
    
    
    def _process_similars(self, similars):
        
        self._logger.info('Processing similar news...')
        self._dao.persist_similar_news(similars)
        
        for similar_news in similars:
            
            id_news = similar_news[0]
            news_url, agency_name = self._dao.get_agency_name_and_url_of_checked_news(similar_news[3])
            
            with InterventorJobSocialMedia(config.SCHEDULE.QUEUE.INTERVENTOR_SEND_ALERT_TO_SOCIAL_MEDIA, \
                lambda: assign_interventor_jobs_to_pickle_file()) as job:
                
                try:
                    text_news_cleaned = self._dao.get_clean_text_news_from_id(id_news)
                    title = text_news_cleaned.upper() if len(text_news_cleaned) < 6 else " ".join(text_news_cleaned.split()[:6]).upper()
                    
                    payload = str(dict(zip(job[1].payload_keys, \
                        (f"❌ NOTÍCIA IDENTIFICADA COMO FAKE NEWS POR {SocialMediaAlertType.SIMILARIDADE.name} NO SITE DA AGÊNCIA {agency_name} - {title}...", "", f"Saiba mais em: {news_url}"))))
                    
                    id = job[1].create_job(self._dao, payload)
                    self._logger.info(f"{job[0]} {config.SCHEDULE.INTERVENTOR_JOBS_FILE}: job {id} persisted successfully.")            
            
                except Exception as e:
                    self._logger.error(e)
    
    
    def _process_candidates_to_check(self, candidates_to_check):
        
        self._logger.info('Processing news to be checked...')
        curated = False
        
        if config.INTERVENTOR.CURATORSHIP:
            
            curated = [c for c in candidates_to_check if c[3] != None]
            candidates_to_check = [c for c in candidates_to_check if c[3] == None]
        
            if curated:
                self._process_labeled_curatorship(curated)
        
            if not candidates_to_check:
                return
        
        candidates_id = [c[0] for c in candidates_to_check]
        
        for agency in config.INTERVENTOR.FACT_CHECK_AGENCIES:            
            id_trusted_agency,_,_,_ = self._dao.get_data_from_agency(agency)
        
            for id_news in candidates_id:                    
                
                try: # só pode haver uma tupla única de 'id_news' e 'id_trusted_agency' na tabela 'checking_outcome'.
                    self._dao.persist_candidates_to_check(id_news, id_trusted_agency)
                
                except UniqueViolation as e:
                    error = e.args[0].replace('\n', ' ')
                    self._logger.error(f"News with id {id_news} and FCA's id {id_trusted_agency} already exists in table 'detectenv.checking_outcome', thus violating the unique constraint pair: {error}")
        
        message, xlsx_path = InterventorDAO.build_excel_spreadsheet([candidate[:2] for candidate in candidates_to_check])
        self._logger.info(message)
    
        # cria jobs de alertas para a rede social das notícias enviadas por email para as FCAs.
        for candidate_news in candidates_to_check:
            
            with InterventorJobFCA(config.SCHEDULE.QUEUE.INTERVENTOR_SEND_ALERT_TO_SOCIAL_MEDIA, \
            assign_interventor_jobs_to_pickle_file) as job_media:
                
                try:
                    text_news_cleaned = self._dao.get_clean_text_news_from_id(candidate_news[0])
                    title = text_news_cleaned.upper() if len(text_news_cleaned) < 6 else " ".join(text_news_cleaned.split()[:6]).upper()
                    payload = str(dict(zip(job_media[1].payload_keys, \
                        (f"⚠️ {SocialMediaAlertType.DETECTADO.name} COMO POSSÍVEL FAKE NEWS - {title}...", TextPreprocessing.slugify(title.lower()), text_news_cleaned))))
                    
                    id = job_media[1].create_job(self._dao, payload)
                    self._logger.info(f"{job_media[0]} {config.SCHEDULE.INTERVENTOR_JOBS_FILE}: job {id} persisted successfully.")            
            
                except Exception as e:
                    self._logger.error(e)
                            
        # cria job para envio de email para as ACFs.
        with InterventorJobFCA(config.SCHEDULE.QUEUE.INTERVENTOR_SEND_NEWS_TO_FCA, \
            assign_interventor_jobs_to_pickle_file) as job:
            
            for fca in config.INTERVENTOR.FACT_CHECK_AGENCIES:
            
                fca_info = self._dao.get_data_from_agency(fca)
                payload = str(dict(zip(job[1].payload_keys, [fca_info[1], xlsx_path, len(candidates_id)])))
                
                id = job[1].create_job(self._dao, payload)
                self._logger.info(f"{job[0]} {config.SCHEDULE.INTERVENTOR_JOBS_FILE}: job {id} persisted successfully.")
        
        
    def _split_similar_news(self, news):
        """Split the news list into two ones: (i) list of similars and (ii) list of not similars.
        
        Identify records on news list that is similar to early published by FCA.
        Add FCA id news to those identified as similar.

        Args:
            news (list): list of news
        
        Returns:
            tuple: (list of similars, list of not similars)
        """
        
        similars, not_similars = list(), list()
        
        for i, (_, text_news, _) in enumerate(news):
            text_news_cleaned = self._text_preprocessor.text_cleaning(text_news)
        
            for id_news_checked, _, _, publication_title_cleaned in self._all_fca_news:
                is_similar, _ = self._text_preprocessor.check_duplications(text_news_cleaned, publication_title_cleaned)
        
                if is_similar:
                    similars.append(news[i] + (id_news_checked,))
                    break
            else:
                not_similars.append(news[i])
        
        return (similars, not_similars)
                
                
    def _process_labeled_curatorship(self, curated):
        
        news = [(c[0], c[3]) for c in curated]
        self._dao.update_ground_truth_label(news)
        fake_news = [c[0] for c in curated if c[3]]
        
        for news in fake_news:
            
            with InterventorJobSocialMedia(config.SCHEDULE.QUEUE.INTERVENTOR_SEND_ALERT_TO_SOCIAL_MEDIA, \
                lambda: assign_interventor_jobs_to_pickle_file()) as job:
                
                try:
                    text_news_cleaned = self._dao.get_clean_text_news_from_id(news)
                    title = text_news_cleaned.upper() if len(text_news_cleaned) < 6 else " ".join(text_news_cleaned.split()[:6]).upper()
                    payload = str(dict(zip(job[1].payload_keys, \
                        (f"❗ {SocialMediaAlertType.CONFIRMADO.name} COMO FAKE NEWS POR CURADORIA - {title}...", TextPreprocessing.slugify(title.lower()), text_news_cleaned))))
                    
                    id = job[1].create_job(self._dao, payload)
                    self._logger.info(f"{job[0]} {config.SCHEDULE.INTERVENTOR_JOBS_FILE}: job {id} persisted successfully.")            
            
                except Exception as e:
                    self._logger.error(e)

    
    def _get_all_agency_news(self):
        
        all_fca_news = self._dao.get_all_agency_news()
        
        for i, (_, publication_title, _) in enumerate(all_fca_news):
            all_fca_news[i] += (self._text_preprocessor.text_cleaning(publication_title),)
            
        return all_fca_news