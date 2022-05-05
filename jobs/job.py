import abc
import datetime
from pathlib import Path
import pandas as pd
from typing import List, Tuple
from src.config import Config as config

class Job:

    def __init__(self, schedule_type: config.SCHEDULE.QUEUE) -> None:
        """Abstract base class representation for creating specific concrete classes to persist different jobs in the database.

        Args:
            schedule_type (config.SCHEDULE.QUEUE): the type of job belonging to a particular queue.
        """
        
        self.id_job: int = 0
        self.id_failed_job = 0
        self.payload: str = ""
        self.attempts: int = 0
        self.error_message: str = ""
        self.queue = schedule_type.name
        self.created_at: datetime.datetime = pd.NaT
        self.updated_at: datetime.datetime = pd.NaT
        self.periodicity: int = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["periodicity"]
        self.max_attempts: int = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["max_attempts"]
        self.payload_keys: Tuple[str] = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["payload_keys"]
        
        
    def __str__(self) -> str:
        return f"Job {self.id_job}, queue: {self.queue}, created at: {self.created_at}."
        
    
    @abc.abstractmethod
    def create_job(self, dao, **payload_kwargs) -> None:
        """Persists the job on its corresponding queue in the database.
        
        Args:
            dao: a DAO instance related to the respective module;
            payload_args: the payload content that will be stored as JSON format.
        """
        ...
        

class JobManager(abc.ABC):
    
    def __init__(self, job: Job, file_path: str) -> None:
        """Abstract base classe representation for creating specific classes responsible for managing and executing a job. 

        Args:
            job (Job): An instance of a job to be managed or executed.
            file_path (str): a Path object with the location where the serialized file containing all the jobs will be saved for being loaded later by the scheduler.
        """
        self._job = job
        self.file_path = file_path
        
    
    def __str__(self) -> str:
        return f"{self._job.queue} - Nº {self._job.id_job}"
    
    
    def get_id_job(self) -> int:
        return self._job.id_job
    
    
    @abc.abstractmethod
    def check_number_of_max_attempts(self) -> bool:
        ...

    @abc.abstractmethod
    def manage_failed_job(self) -> None:
        ...

    @abc.abstractmethod        
    def run_manager(self) -> bool:
        ...
    
    