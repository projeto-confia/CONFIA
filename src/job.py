import abc
import datetime
import pandas as pd
from typing import Tuple
from src.config import Config as config

class Job(abc.ABC):

    def __init__(self, schedule_type: config.SCHEDULE.QUEUE) -> None:
        """Abstract base class representation for creating specific concrete classes to persist different jobs in the database.

        Args:
            schedule_type (config.SCHEDULE.QUEUE): the type of job belonging to a particular queue.
        """
        
        self.id: int = 0
        self.payload: str = ""
        self.attempts: int = 0
        self.error_message: str = ""
        self.queue = schedule_type.name
        self.created_at: datetime.datetime = pd.NaT
        self.updated_at: datetime.datetime = pd.NaT
        self.periodicity: int = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["periodicity"]
        self.max_attempts: int = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["max_attempts"]
        self.payload_keys: Tuple[str] = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["payload_keys"]
        
    
    @abc.abstractmethod
    def create_job(self, dao, **payload_kwargs) -> None:
        """Persists the job on its corresponding queue in the database.
        
        Args:
            dao: a DAO instance related to the respective module;
            payload_args: the payload content that will be stored as JSON format.
        """
        ...
        

class Job_Manager(abc.ABC):
    
    def __init__(self, job: Job) -> None:
        """Abstract base classe representation for creating specific classes responsible to manage and execute a job. 

        Args:
            job (Job): An instance of a job to be managed or executed.
        """
        self._job = job
        
    def __str__(self) -> str:
        return f"{self.queue} - Nº {self._job.id} executed successfully."
    
    @abc.abstractmethod
    def _check_number_of_max_attempts(self) -> bool:
        ...

    @abc.abstractmethod
    def manage_failed_job(self) -> None:
        ...

    @abc.abstractmethod        
    def run_manager(self) -> bool:
        ...