from jobs.job import Job
from datetime import datetime
from src.config import Config as config
from src.orm.db_wrapper import DatabaseWrapper


def get_job(id_job: int) -> tuple[str]:
        try:
            sql_str = "select * from detectenv.job where id_job = %s;"
            
            with DatabaseWrapper() as db:
                job = db.query(sql_str, (id_job,))
            
            return job[0]
        
        except:
            raise
    
    
def get_failed_job(id_job: int) -> tuple[str]:
    try:
        sql_str = "select * from detectenv.failed_job where id_job = %s;"
        
        with DatabaseWrapper() as db:
            job = db.query(sql_str, (id_job,))
        
        return job[0]
    
    except:
        raise


def get_all_interventor_jobs() -> list[Job]:
    """Selects from Job table all the jobs regarding the Interventor module.
        
    Returns:
        A list containing all the jobs related to the Interventor module.
    """
    
    try:
        sql_str = "select * from detectenv.job where queue ~ '^INTERVENTOR\w{1,}$';"
        jobs = []            
        
        with DatabaseWrapper() as db:
            results = db.query(sql_str)
            
        for result in results:
            job = Job(config.SCHEDULE.QUEUE[result[1]])
            job.id_job = result[0]
            job.payload = result[2]
            job.attempts = result[3]
            job.created_at = result[4]
            job.updated_at = result[5]
            
            jobs.append(job)
        
        return jobs            
    
    except:
        raise


def get_all_fcmanager_jobs() -> list[Job]:
    """Selects from Job table all the jobs regarding the FactCheckManager module.
        
    Returns:
        A list containing all the jobs related to the FactCheckManager module.
    """
    
    try:
        sql_str = "select * from detectenv.job where queue ~ '^FCAMANAGER\w{1,}$';"
        jobs = []            
        
        with DatabaseWrapper() as db:
            results = db.query(sql_str)
            
        for result in results:
            job = Job(config.SCHEDULE.QUEUE[result[1]])
            job.id_job = result[0]
            job.payload = result[2]
            job.attempts = result[3]
            job.created_at = result[4]
            job.updated_at = result[5]
            
            jobs.append(job)
        
        return jobs            
    
    except:
        raise

    

def get_all_fcmanager_failed_jobs() -> list[Job]:
    """Selects from Failed_Job table all the jobs regarding the Interventor module.
        
    Returns:
        A list containing all the jobs related to the FactCheckManager module.
    """
    
    try:
        sql_str = "select * from detectenv.failed_job where queue ~ '^FCAMANAGER\w{1,}$';"
        jobs = []
        
        with DatabaseWrapper() as db:
            results = db.query(sql_str)
        
        for result in results:
            job = Job(config.SCHEDULE.QUEUE[result[2]])
            job.id_failed_job = result[0]
            job.id_job = result[1]
            job.payload = result[3]
            job.attempts = result[4]
            job.created_at = result[5]
            job.updated_at = result[6]
            job.error_message = result[7]
            
            jobs.append(job)
        
        return jobs           
    
    except:
        raise


def get_all_interventor_failed_jobs(self) -> list[Job]:
    """Selects from Failed_Job table all the jobs regarding the Interventor module.
        
    Returns:
        A list containing all the jobs related to the Interventor module.
    """
    
    try:
        sql_str = "select * from detectenv.failed_job where queue ~ '^INTERVENTOR\w{1,}$';"
        jobs = []
        
        with DatabaseWrapper() as db:
            results = db.query(sql_str)
        
        for result in results:
            job = Job(config.SCHEDULE.QUEUE[result[2]])
            job.id_failed_job = result[0]
            job.id_job = result[1]
            job.payload = result[3]
            job.attempts = result[4]
            job.created_at = result[5]
            job.updated_at = result[6]
            job.error_message = result[7]
            
            jobs.append(job)
        
        return jobs           
    
    except:
        raise
    

def get_all_jobs_based_on_queue(queue_type: config.SCHEDULE.QUEUE) -> list[tuple]:
    """Selects from Job table all the jobs concerning the queue named 'queue_type'.
    
    Args:
        queue_type (config.SCHEDULE.QUEUE): the name of the queue containing the jobs to be selected.
        
    Returns:
        A list containing all the jobs related to 'queue_type'.
    """
    
    try:
        sql_str = "SELECT * FROM detectenv.job WHERE queue = %s;"
        
        with DatabaseWrapper() as db:
            jobs = db.query(sql_str, (queue_type.name,))
        return jobs            
    
    except:
        raise


def get_all_failed_jobs_based_on_queue(queue_type: config.SCHEDULE.QUEUE) -> list[tuple]:
    """Selects from Failed_Job table all the failed jobs concerning the queue named 'queue_type'.
    
    Args:
        queue_type (config.SCHEDULE.QUEUE): the name of the queue containing the failed jobs to be selected.
        
    Returns:
        A list containing all the failed jobs related to 'queue_type'.
    """
    
    try:
        sql_str = "SELECT * FROM detectenv.failed_job WHERE queue = %s;"
        
        with DatabaseWrapper() as db:
            failed_jobs = db.query(sql_str, (queue_type.name,))
    
        return failed_jobs
    
    except:
        raise


def create_job(job: Job) -> None:
    """Persists a novel job instance in the Job table.

    Args:
        job (Job): a Job object containing all the information regarding the novel job to be persisted.
        
    Returns:
        id_job (Job): the identifier created for the new job.
    """
    try:
        sql_str = "INSERT INTO detectenv.job (queue, payload) VALUES (%s, %s) RETURNING id_job;"
                    
        with DatabaseWrapper() as db:
            db.execute(sql_str, (job.queue, job.payload,))
            id = db.fetchone()
    
        return id
    
    except:
        raise
    
    
def create_failed_job(job: Job) -> tuple[int]:
    """Persists a novel job instance in the Job table.

    Args:
        job (Job): a Job object containing all the information regarding the novel job to be persisted.
        
    Returns:
        id_failed_job (Job): the identifier created for the new failed job.
    """
    try:
        sql_str = "INSERT INTO detectenv.failed_job (id_job, queue, payload, attempts, created_at, error_message) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_failed_job;"
                    
        with DatabaseWrapper() as db:
            try:
                db.execute(sql_str, (job.id_job, job.queue, job.payload, job.attempts, datetime.now(), str(job.error_message.args,)))
            except AttributeError:
                db.execute(sql_str, (job.id_job, job.queue, job.payload, job.attempts, datetime.now(), str(job.error_message,)))
            
            id = db.fetchone()
    
        return id
    
    except:
        raise
    

def update_number_of_attempts_job(job: Job) -> None:
    """Increments the number of attempts of a particular job after trying to execute it without success. The field 'updated_at' is also updated with the current time when the attempt actually occurred.
    
    Args:
        job (Job): the job that is being updated.
    """
    
    try:
        sql_str = "UPDATE detectenv.job SET attempts = %s, updated_at = %s WHERE id_job = %s;"
        
        with DatabaseWrapper() as db:
            db.execute(sql_str, (job.attempts, datetime.now(), job.id_job,))
    
    except:
        raise
    

def update_number_of_attempts_failed_job(failed_job: Job) -> None:
    """Increments the number of attempts of a particular failed job after trying to execute it without success. The field 'updated_at' is also updated with the current time when the attempt actually occurred.
    
    Args:
        failed_job (Job): the failed job that is being updated.
    """
    
    try:
        sql_str = "UPDATE detectenv.failed_job SET attempts = %s, updated_at = %s, error_message = %s WHERE id_job = %s;"
        
        with DatabaseWrapper() as db:
            db.execute(sql_str, (failed_job.attempts, datetime.now(), failed_job.error_message.args, failed_job.id_job,))
    
    except:
        raise


def delete_job(id_job: int) -> tuple:
    """Deletes a job from the Job table and returns its information.

    Args:
        id_job (int): the id of the job to be deleted from Job table.
        
    Returns:
        a tuple containing all the attributes regarding the deleted job.
    """
    
    sql_str = "DELETE FROM detectenv.job WHERE id_job = %s RETURNING *;"
    
    try:
        with DatabaseWrapper() as db:
            db.execute(sql_str, (id_job,))
            job = db.fetchone()
            
        return job
    
    except:
        raise
    
        
def delete_failed_job(id_job: int) -> tuple:
    """Deletes a job from the Failed_Job table and returns its original identifier (id_job).

    Args:
        id_failed_job (int): the id of the failed job to be deleted from Failed_Job table.
        
    Returns:
        a tuple containing the original identifier of the job deleted from Failed_Job.
    """
    
    sql_str = "DELETE FROM detectenv.failed_job WHERE id_job = %s RETURNING *;"
    
    try:
        with DatabaseWrapper() as db:
            db.execute(sql_str, (id_job,))
            job = db.fetchone()
            
        return job
    
    except:
        raise