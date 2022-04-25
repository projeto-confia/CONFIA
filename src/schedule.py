from typing import List
from dataclasses import field
from src.job import Job_Manager
from src.interventor.facade import InterventorFacade

class Schedule(object):
    
    _failed_jobs: int = 0
    _subscribed_jobs: List[Job_Manager] = field(default_factory=list)
    
    @staticmethod
    def subscribe_job(job: Job_Manager) -> None:
        Schedule._subscribed_jobs.append(job)
    
    @staticmethod
    def run():
        # InterventorFacade().run_manager()
        if not len(Schedule._subscribed_jobs):
            print("There are no scheduled jobs to be executed.")
            
        else:
            for job_manager in Schedule._subscribed_jobs:
                if not job_manager.run_manager():
                    job_manager.manage_failed_job()
                    Schedule._failed_jobs += 1
                    
        Schedule._subscribed_jobs = []
                
                
if __name__ == '__main__':
    print('Starting schedule...')
    Schedule.run()
