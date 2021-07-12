import time
from random import randint

from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler
from getDomainAge.models.enums import JobStatus
from getDomainAge.services.domain import DomainService
from getDomainAge.services.email import EmailService
from getDomainAge.services.job import JobService


class WorkerService():
    """
    Worker class for handling jobs
    """
    def __init__(self):
        self.__env = Environment()
        self.__logger = LogHandler.get_logger(__name__, self.__env.log_path)
        self.__job_service = JobService()
        self.__domain_service = DomainService()
        self.__logger.info('Worker service initialized')

    def run(self):
        """
        Method to start the worker service.
        This method is suppose to be invoked in thread.
        It will checked for new jobs which are present in the job cache and which are in pending state.

        Next it will pick the jobs one by one and will complete those
        """
        # waiting for 5s for starting the worker loop
        time.sleep(5)

        # updating job cache
        self.__job_service.udpate_cache()

        email_service = EmailService()
        self.__logger.info('Starting worker service')
        while True:
            is_running = False
            pending_job = self.__job_service.get_pending_job()
            wait_time = randint(1, 10)

            if pending_job and not is_running:
                is_running = True
                self.__logger.info(f'A new pending job detected, picking job #{pending_job.id}')

                # updating status to running
                self.__job_service.update_job_status(pending_job.id, JobStatus.RUNNING)

                # fetching results
                csv_results = self.__domain_service.get_age_from_urls(pending_job.urls.split(','))

                # saving results
                ouptut_filepath = self.__job_service.save_result(pending_job.id, csv_results)

                # emailing results
                mail_status = email_service.send_email(pending_job.id, pending_job.requested_by, ouptut_filepath)

                if mail_status:
                    # updating status to completed
                    self.__job_service.update_job_status(pending_job.id, JobStatus.COMPLETED)
                else:
                    self.__job_service.update_job_status(pending_job.id, JobStatus.FAILED_EMAIL)

                self.__logger.info(f'Completed processing of job #{pending_job.id}')

            time.sleep(wait_time)
