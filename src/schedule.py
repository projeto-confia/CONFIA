import datetime
from typing import Dict
from jobs.job import JobManager
import logging, pickle, pathlib
from src.config import Config as config
from src.engine.engine import EngineManager


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
        
        if len(Schedule._subscribed_jobs_dict):
            
            for id, job_manager in Schedule._subscribed_jobs_dict.items():
                
                try:
                    last_update = job_manager.job.__dict__["updated_at"]
                    job_periodicity = job_manager.job.__dict__["periodicity_in_minutes"]
                    
                    allowed_period_to_consume_job = last_update + datetime.timedelta(minutes=job_periodicity)
                    
                    if datetime.datetime.now() < allowed_period_to_consume_job:                        
                        continue    
                    
                    _ = job_manager.run_manager()
                    
                
                except Exception:
                    Schedule._subscribed_failed_jobs_dict[id] = job_manager
                    
                    message = job_manager.manage_failed_job()
                    
                    if len(message):
                        Schedule._logger.info(message)                    
                    

if __name__ == '__main__':
    
    init_log(verbose=config.LOGGING.VERBOSE)
    EngineManager().run()
    Schedule.run()
