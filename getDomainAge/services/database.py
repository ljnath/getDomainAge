from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler
from getDomainAge.models.database.tables import Job
from getDomainAge.services.notification import NotificationService
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class DatabaseService:
    """
    Class responsible for all kind of database service
    """
    def __init__(self):
        self.__env = Environment()
        self.__logger = LogHandler.get_logger(__name__, self.__env.log_path)

        # creating SQLAlchemy DB engine, if it is not created before
        # there should be a single DB engine, therefore stroing the instance as an environment property
        # using SQLite as database
        if not self.__env.sqlalchemy_engine:
            self.__env.sqlalchemy_engine = create_engine(f'sqlite:///{self.__env.db_path}', echo=False)

        # cerating a database session
        self.__session = Session(bind=self.__env.sqlalchemy_engine)

    def initialize(self) -> None:
        """
        method to initialize the database
        Initialization process includes creation of all DB tables and commiting the changes
        """
        self.__env.sqlalchemy_base.metadata.create_all(self.__env.sqlalchemy_engine)
        self.__logger.info('Successfully initialized database')

    def get_job_by_id(self, job_id) -> Job:
        """
        method to search for a single Job record for id and return it
        :return Job : result job record
        """
        return self.__session.query(Job).filter_by(id=job_id).first()

    def get_all_jobs_by_requestor(self, requestor) -> list:
        """
        method to search for al Job records requested by requestor and return it
        :return Jobs : list of jobs
        """
        return self.__session.query(Job).filter_by(requestor=requestor)

    def get_all_jobs(self) -> list:
        """
        method to search for all records of job in the database and return it as a list

        Here instead of using the existing session, a new session is created because 'SQLite objects created in a thread can only be used in that same thread'
        :return result : list of all job records
        """
        self.__logger.info('Fetching all job records from databse')
        with Session(bind=self.__env.sqlalchemy_engine) as local_session:
            return local_session.query(Job).all()

    def add_job(self, job):
        """
        method to add a new Job in the database
        :param job: new Job record to add into the database
        """
        try:
            with Session(bind=self.__env.sqlalchemy_engine) as local_session:
                local_session.add(job)
                local_session.commit()
                self.__logger.info('Successfully commited database with new Job')
        except Exception as e:
            NotificationService().notify_failure('Failed to add your job because of a database error. Please try again')
            self.__logger.error('Failed to add job because of database error')
            self.__logger.exception(e, exc_info=True)

        # except sqlite3.OperationalError:
        #     NotificationService().notify_failure('Failed to add your job because of a database error. Please try again')
