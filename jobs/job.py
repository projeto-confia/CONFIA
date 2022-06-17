import abc
import datetime
import pandas as pd
from src.config import Config as config
from typing import Any, Callable, Tuple

class Job:

    def __init__(self, schedule_type: config.SCHEDULE.QUEUE, fn_update_pickle_file: Callable[[], None] = None) -> None:
        """Abstract base class representation for creating specific concrete classes to persist different jobs in the database.

        Args:
            schedule_type (config.SCHEDULE.QUEUE): the type of job belonging to a particular queue.
            fn_update_pickle_file: (Callable([Any],None)): a function containing a dao object for synchronizing the pickle object of the module with the Job table.
        """
        
        self.id_job: int = 0
        self.id_failed_job = 0
        self.payload: str = ""
        self.attempts: int = 0
        self.error_message: str = ""
        self.queue = schedule_type.name
        self.created_at: datetime.datetime = pd.NaT
        self.updated_at: datetime.datetime = pd.NaT
        self.max_attempts: int = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["max_attempts"]
        self.payload_keys: Tuple[str] = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["payload_keys"]
        self.periodicity_in_minutes: int = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["periodicity_in_minutes"]
        
        self.fn_update_pickle_file = fn_update_pickle_file
        
        
    def __str__(self) -> str:
        return f"Job {self.id_job}, queue: {self.queue}, created at: {self.created_at}."
    
    
    def __enter__(self) -> Tuple[str, Any]:
        return f"Creating/updating file", self
    
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            self.fn_update_pickle_file()
        except:
            raise
            
    @abc.abstractmethod
    def create_job(self, dao, payload: dict) -> None:
        """Persists the job on its corresponding queue in the database.
        
        Args:
            dao: a DAO instance related to the respective module;
            payload: the payload content that will be stored as JSON format.
        """
        ...
        

class JobManager(abc.ABC):
    
    def __init__(self, job: Job, file_path: str) -> None:
        """Abstract base classe representation for creating specific classes responsible for managing and executing a job. 

        Args:
            job (Job): An instance of a job to be managed or executed.
            file_path (str): a Path object with the location where the serialized file containing all the jobs will be saved for being loaded later by the scheduler.
        """
        self.job = job
        self.file_path = file_path
        
    
    def __str__(self) -> str:
        return f"{self.job.queue} - Nº {self.job.id_job}"
    
    
    @property
    def get_id_job(self) -> int:
        return self.job.id_job
    
    
    @abc.abstractmethod
    def check_number_of_max_attempts(self) -> bool:
        """Checks whether the number of attempts has exceeded.

        Returns:
            bool: returns True if the number of attempts has maxed out the limit of the queue; False otherwise.
        """
        ...

    @abc.abstractmethod
    def manage_failed_job(self) -> str:
        ...

    @abc.abstractmethod        
    async def run_manager(self) -> str:
        ...
    
    