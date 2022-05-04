import logging
from typing import Dict
from src.job import JobManager
from src.config import Config as config
# from src.interventor.facade import InterventorFacade

class Schedule:
    
    _failed_jobs: int = 0
    _subscribed_jobs: Dict[int, JobManager] = {}
    _subscribed_failed_jobs: Dict[int, JobManager] = {}
    _logger = logging.getLogger(config.LOGGING.NAME)
    
    
    @staticmethod
    def subscribe_job(job_manager: JobManager) -> None:
        id = job_manager.return_id_job()
        if id not in Schedule._subscribed_jobs:
            Schedule._subscribed_jobs[id] = job_manager
            Schedule._logger.info(f"Job {id} has been scheduled.")
        
    
    @staticmethod
    def subscribe_failed_job(job_manager: JobManager) -> None:
        id = job_manager.return_id_job()
        if id not in Schedule._subscribed_failed_jobs:
            Schedule._subscribed_failed_jobs[id] = job_manager
            Schedule._logger.info(f"Job {id} has been scheduled.")
    
    
    @staticmethod
    def run():
        # InterventorFacade().run_manager()
        if not len(Schedule._subscribed_jobs):
            Schedule._logger.info("There are no scheduled jobs to be executed.")
            
        if not len(Schedule._subscribed_failed_jobs):
            Schedule._logger.info("There are no scheduled failed_jobs to be executed.")
            
        else:
            for id, job_manager in Schedule._subscribed_jobs.items():
                
                if not job_manager.run_manager():
                    job_manager.manage_failed_job()                    
                    Schedule._failed_jobs += 1
                    
                else:
                    del Schedule._subscribed_jobs[id]
                    
            for _, job_manager in Schedule._subscribed_failed_jobs.items():
                
                if not job_manager.run_manager():
                    job_manager.manage_failed_job()                    
                    Schedule._failed_jobs += 1
                    
                else:
                    del Schedule._subscribed_failed_jobs[id]
        
        Schedule._logger.info("--- Message to failed jobs to be completed... ---")
        Schedule._failed_jobs = 0
                
if __name__ == '__main__':
    Schedule._logger.info('Starting schedule...')
    Schedule.run()
