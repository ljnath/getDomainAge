import requests
from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler
from getDomainAge.models.enums import Endpoint, HttpHeader


class JobService:
    """
    Class responsible for all services related to Job
    """
    def __init__(self):
        self.__env = Environment()
        self.__logger = LogHandler.get_logger(self.__env.app_name, self.__env.log_path)

    def update_job_cache(self) -> None:
        """
        Method to update the job cache.
        This is achieved by making a POST call to the ../reloadCache endpoint
        """
        if not self.__env.cached_jobs:
            requests.post(
                url=f'http://127.0.0.1:{self.__env.server_port}{Endpoint.RELOAD_CACHE.value}',
                headers={HttpHeader.API_KEY.value: self.__env.api_secrect_key})
            self.__logger.info('Successfuly updated job cache')
