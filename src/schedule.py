from typing import Dict
from jobs.job import JobManager
import logging, pickle, pathlib
from src.config import Config as config


def init_log(verbose=False):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(config.LOGGING.SCHEDULER_FILE_PATH)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    if verbose:
        stream_format = logging.Formatter('%(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.NOTSET)
        stream_handler.setFormatter(stream_format)
        logger.addHandler(stream_handler)
        

class Schedule:
    
    _subscribed_jobs_dict: Dict[int, JobManager] = {}
    _subscribed_failed_jobs_dict: Dict[int, JobManager] = {}
    _logger = logging.getLogger(__name__)
            
            
    @staticmethod
    def load_all_jobs() -> None:
        
        for jobs in pathlib.Path('jobs/').glob('*.pkl'):
            with open(jobs, 'rb') as file:
                jobs_dict = pickle.load(file)
                Schedule._subscribed_jobs_dict.update(jobs_dict)

    
    @staticmethod
    def run():
        
        Schedule.load_all_jobs()
        
        if not len(Schedule._subscribed_jobs_dict):
            Schedule._logger.info("There aren't scheduled jobs to be executed.")
            
        else:
            for id, job_manager in Schedule._subscribed_jobs_dict.items():
                
                Schedule._logger.info(f"Running job {job_manager}...")
                
                if not job_manager.run_manager():
                    #! verificar número máximo de tentativas para, se for o caso, migrar os jobs para a tabela 'failed_jobs'.
                    Schedule._subscribed_failed_jobs_dict[id] = job_manager
                    job_manager.manage_failed_job()
                    
                else:
                    #! apagar job do banco de dados.
                    Schedule._logger.info(f"Job {job_manager} has been executed successfully.")
        
        # Schedule._logger.info("--- Message to failed jobs to be completed... ---")
        
                
if __name__ == '__main__':
    init_log(verbose=config.LOGGING.VERBOSE)
    Schedule._logger.info('Starting schedule...')
    Schedule.run()
