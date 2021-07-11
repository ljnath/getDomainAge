from time import time

from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler
from getDomainAge.models.database.tables import Job
from getDomainAge.models.enums import JobStatus
from getDomainAge.services.database import DatabaseService


class JobService:
    """
    Class responsible for all services related to Job
    """
    def __init__(self):
        self.__env = Environment()
        self.__logger = LogHandler.get_logger(__name__, self.__env.log_path)
        self.__db_service = DatabaseService()

    def add_new_job(self, urls, requested_by):
        status = False
        try:
            # adding the new job in the database and notifying user
            new_job = Job(
                requested_by=requested_by,
                requested_on=int(time()),
                status=JobStatus.PENDING.value,
                urls=','.join(urls))
            self.__db_service.add_job(new_job)
            status = True
            self.__logger.info(f'User {requested_by} has added a new job with {len(urls)} URLs')

            # updating job cache after adding a new job
            self.update_job_cache()
        except Exception as e:
            self.__logger.exception(f'Failed to add new job. Error: {e}')

        return status

    def get_all_jobs(self, from_cache=True) -> list:
        """
        Method to get list of all job
        :param from_cache : bool value indicating is the result needs to be fetch from cache rather then actual database
        :return jobs : list of valid jobs
        """
        jobs = []
        if from_cache:
            jobs = self.__env.memcached_jobs
        else:
            jobs = self.__db_service.get_all_jobs()

        self.__logger.info(f'Fetched {len(jobs)} jobs from {"cache" if from_cache else "database"}')
        return jobs

    def get_job_by_requestor(self, requestor, from_cache=True) -> list:
        """
        Method to get list of job filtered by requestor
        :param requestor : string filter by criteria, email of user
        :param from_cache : bool value indicating is the result needs to be fetch from cache rather then actual database
        :return jobs : list of valid jobs
        """
        jobs = []
        if from_cache:
            jobs = [job for job in self.__env.memcached_jobs if job.requested_by.lower() == requestor]
        else:
            jobs = self.__db_service.get_all_jobs_by_requestor(requestor)

        self.__logger.info(f'Fetched {len(jobs)} jobs requested by user {requestor} from {"cache" if from_cache else "database"}')
        return jobs

    def update_job_cache(self) -> None:
        """
        Method to update the job cache.
        This is achieved by making a POST call to the ../reloadCache endpoint
        """
        self.__env.memcached_jobs = self.__db_service.get_all_jobs()
