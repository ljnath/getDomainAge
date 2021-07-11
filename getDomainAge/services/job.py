import requests
from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler
from getDomainAge.models.enums import Endpoint, HttpHeader
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
                requested_on=123456,
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

    def update_job_cache(self) -> None:
        """
        Method to update the job cache.
        This is achieved by making a POST call to the ../reloadCache endpoint
        """
        requests.post(
            url=f'http://127.0.0.1:{self.__env.server_port}{Endpoint.RELOAD_CACHE.value}',
            headers={HttpHeader.API_KEY.value: self.__env.api_secrect_key})
        self.__logger.info('Successfuly updated job cache')
