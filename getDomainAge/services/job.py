import csv
from time import time

from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler
from getDomainAge.models.database.tables import Jobs
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
            new_job = Jobs(
                requested_by=requested_by,
                requested_on=int(time()),
                status=JobStatus.PENDING.value,
                urls=','.join(urls))
            self.__db_service.add_job(new_job)
            status = True
            self.__logger.info(f'User {requested_by} has added a new job with {len(urls)} URLs')

            # updating job cache after adding a new job
            self.udpate_cache()
        except Exception as e:
            self.__logger.exception(f'Failed to add new job. Error: {e}')

        return status

    def get_output_filepath(self, job_id: int) -> str:
        """
        Method to generate the output filepath of the results
        :param job_id : job_id for which the output filepath needs to be generated
        :return filepath : path of the file where the result of job_id will be saved
        """
        return f'{self.__env.result_directory}/job_id_{job_id}.csv'

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

    def get_job_by_id(self, id: int, from_cache=True) -> Jobs:
        """
        Method to get job filtered by id
        :param id : string ID of the job
        :param from_cache : bool value indicating is the result needs to be fetch from cache rather then actual database
        :return result_job : instance of Job which matches the ID
        """
        self.__logger.debug(f'Trying to fetch job with id={id} and from_cache={from_cache}')
        result_job = None
        if from_cache:
            for job in self.__env.memcached_jobs:
                if job.id == id:
                    result_job = job
                    break
        else:
            result_job = self.__db_service.get_job_by_id(id)

        return result_job

    def get_job_by_requestor(self, requestor, from_cache=True) -> list:
        """
        Method to get list of job filtered by requestor
        :param requestor : string filter by criteria, email of user
        :param from_cache : bool value indicating is the result needs to be fetch from cache rather then actual database
        :return jobs : list of valid jobs
        """
        self.__logger.debug(f'Trying to fetch job by requestor with requestor={requestor} and from_cache={from_cache}')
        jobs = []
        if from_cache:
            jobs = [job for job in self.__env.memcached_jobs if job.requested_by.lower() == requestor]
        else:
            jobs = self.__db_service.get_all_jobs_by_requestor(requestor)

        self.__logger.info(
            f'Fetched {len(jobs)} jobs requested by user {requestor} from {"cache" if from_cache else "database"}')
        return jobs

    def get_pending_job(self, from_cache=True) -> Jobs:
        """
        Method to get the 1st pending job either from the cache or from database depending on the input parameter
        :param from_cache : bool value indicating is the result needs to be fetch from cache rather then actual database
        :return job : instance of Job which is in pending state
        """
        # self.__logger.debug(f'Trying to fetch the first pending job; from_cache={from_cache}')
        result_job = None
        if from_cache:
            for job in self.__env.memcached_jobs:
                if job.status == JobStatus.PENDING.value:
                    result_job = job
                    break
        else:
            result_job = self.__db_service.get_pending_job()
        return result_job

    def update_job_status(self, job_id: int, new_status: JobStatus) -> bool:
        job = self.get_job_by_id(job_id)
        temp_status = job.status

        job.status = new_status.value

        if new_status == JobStatus.COMPLETED or new_status == JobStatus.FAILED_EMAIL:
            job.completed_on = int(time())

        self.__db_service.update_job(job)
        self.__logger.info(f'Updated job status for Job #{job_id} from {temp_status} to {new_status.value}')

        # updating job cache after adding a new job
        self.udpate_cache()

    def save_result(self, job_id: int, csv_results: list) -> str:
        """
        method to save job result to file
        :param job_id : Id of the job which needs to be saved
        :param csv_results : list of 'CsvResults'
        :return output_filepath : complete path of the output file
        """
        output_filepath = self.get_output_filepath(job_id)
        with open(output_filepath, 'w', encoding='utf-8', newline='') as file_handler:
            csv_writer = csv.writer(file_handler)
            csv_writer.writerow(['URL', 'Domain Name', 'Age (in days)'])
            _ = [csv_writer.writerow([result.url, result.domain_name, result.age]) for result in csv_results]
            self.__logger.info(f'Successfully saved {len(csv_results)} results from Job #{job_id} to file {output_filepath}')
        return output_filepath

    def udpate_cache(self) -> None:
        """
        Method to update the job cache.
        This is achieved by making a POST call to the ../reloadCache endpoint
        """
        self.__env.memcached_jobs = self.__db_service.get_all_jobs()
