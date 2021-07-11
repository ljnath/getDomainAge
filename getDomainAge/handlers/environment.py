import os
from functools import wraps

from getDomainAge.common.singleton import Singleton
from getDomainAge.handlers.exception import UninitializedEnvironment
from sqlalchemy.orm import declarative_base


class Environment(metaclass=Singleton):
    def __init__(self):
        self.__is_initialized = False
        self.__cached_jobs = None
        self.__sqlalchemy_engine = None
        self.__sqlalchemy_base = declarative_base()

    def __check_environment(class_member):
        """
        Decorator which takes a class member as argument. This argument is wrapped using wraps()
        The inner function takes class instance for accessing the class members. All are argments are accepted using *args and **kwargs
        It checked if the environment is initialized, if yes it calls the class_member with all the input argument; if not it raises an exception
        """
        @wraps(class_member)
        def inner_function(class_inst, *args, **kwargs):
            if not class_inst.__is_initialized:
                raise UninitializedEnvironment()

                # calling class member for processing the calling method
            return class_member(class_inst, *args, **kwargs)

        return inner_function

    def initialize(self, config):
        """
        Method to initialize the environmental variabled with user configuration
        :param config : config as dict. Configuration values in the form of a dictionary
        """
        self.__workspace_path = config['workspace_path']

        self.__server_host = config['server']['host']
        self.__server_port = config['server']['port']
        self.__server_debug_mode = config['server']['debug']

        self.__smtp_host = config['smtp']['host']
        self.__smtp_port = config['smtp']['port']
        self.__smtp_username = config['smtp']['username']
        self.__smtp_password = config['smtp']['password']
        self.__smtp_sender_email = config['smtp']['sender_email']

        self.__app_job_per_page = config['application']['jobs_per_page']
        self.__app_session_timeout = config['application']['session_timeout']

        self.__log_directory = f'{self.__workspace_path}/logs/'
        self.__results_directory = f'{self.__workspace_path}/results/'

        for directory_path in (self.__log_directory, self.__results_directory):
            os.makedirs(directory_path, exist_ok=True)

        self.__is_initialized = True

    @property
    @__check_environment
    def app_name(self):
        return 'getDomainAge'

    @property
    @__check_environment
    def app_version(self):
        return 0.3

    @property
    @__check_environment
    def workspace_path(self):
        return self.__workspace_path

    @property
    @__check_environment
    def db_path(self):
        return f'{self.__workspace_path}/domain.db'

    @property
    @__check_environment
    def cache_path(self):
        return f'{self.__workspace_path}/domain.cache'

    @property
    @__check_environment
    def log_path(self):
        return f'{self.__log_directory}/app.log'

    @property
    @__check_environment
    def result_directory(self):
        return self.__results_directory

    @property
    @__check_environment
    def server_host(self):
        return self.__server_host

    @property
    @__check_environment
    def server_port(self):
        return self.__server_port

    @property
    @__check_environment
    def server_debug_mode(self):
        return self.__server_debug_mode

    @property
    @__check_environment
    def smtp_host(self):
        return self.__smtp_host

    @property
    @__check_environment
    def smtp_port(self):
        return self.smtp_port

    @property
    @__check_environment
    def smtp_username(self):
        return self.__smtp_username

    @property
    @__check_environment
    def smtp_password(self):
        return self.__smtp_password

    @property
    @__check_environment
    def smtp_sender_email(self):
        return self.__smtp_sender_email

    @property
    @__check_environment
    def app_job_per_page(self):
        return self.__app_job_per_page

    @property
    @__check_environment
    def app_session_timeout(self):
        return self.__app_session_timeout

    @property
    @__check_environment
    def cached_jobs(self):
        return self.__cached_jobs

    @cached_jobs.setter
    @__check_environment
    def cached_jobs(self, value):
        self.__cached_jobs = value

    @property
    @__check_environment
    def sqlalchemy_engine(self):
        return self.__sqlalchemy_engine

    @sqlalchemy_engine.setter
    @__check_environment
    def sqlalchemy_engine(self, value):
        self.__sqlalchemy_engine = value

    @property
    @__check_environment
    def sqlalchemy_base(self):
        return self.__sqlalchemy_base

    @property
    @__check_environment
    def whois_url(self):
        return 'https://www.whois.com/whois/'

    @property
    @__check_environment
    def api_secrect_key(self):
        return 'this-is-my-secret-key'
