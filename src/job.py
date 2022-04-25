import abc
from src.config import Config as config

class Job(abc.ABC):

    def __init__(self, schedule_type: config.SCHEDULE.QUEUE) -> None:
        """Abstract base class representation for creating specific classes to persist different jobs in the database.

        Args:
            schedule_type (config.SCHEDULE.QUEUE): the type of job belonging to a particular queue.
        """
        
        self.id: int = 0
        self.payload: str = ""
        self.queue = schedule_type.name
        self._periodicity = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["periodicity"]
        self._description = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["description"]
        self._max_attempts = config.SCHEDULE.SCHEDULE_PARAMS[schedule_type]["max_attempts"]
        
    
    @abc.abstractmethod
    def create_job(self, *args) -> None:
        """Persists the job on its corresponding queue in the database.
        
        Args:
            *args: (list): a list containing custom parameters, such as a DAO instance or other information.
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
        return f"{self.queue} - Nº {self.id} executed successfully."
    
    @abc.abstractmethod
    def _check_number_of_max_attempts(self) -> bool:
        ...

    @abc.abstractmethod
    def manage_failed_job(self) -> None:
        ...

    @abc.abstractmethod        
    def run_manager(self) -> bool:
        ...