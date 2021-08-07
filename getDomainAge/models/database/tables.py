from getDomainAge.handlers.environment import Environment
from sqlalchemy import Column, Integer, String


class Jobs(Environment().sqlalchemy_base):
    """
    Declaring Mapped Classes representing the Job table in the database
    These kind of model classes should inherit from instance of sqlalchemy.orm.declarative_base

    As this is a structured project, the instance of sqlalchemy.orm.declarative_base (Base) is
    created in the DatabaseService and stored in the environemnt class.
    Therefore this class inherits from the Environment().sqlalchemy_base

    TABLE NAME: Jobs
    SCHEMA:
    +--------------+---------------+-----+
    | COLUMN NAME  | DATATYPE      | PK  |
    +--------------+---------------+-----+
    | ID           | Integer       | YES |
    | requested_by | Sring (50)    |     |
    | requested_on | Integer       |     |
    | status       | String(20)    |     |
    | urls         | String(99999) |     |
    | completed_on | Integer       |     |
    +--------------+---------------+-----+
    """

    __tablename__ = 'Jobs'

    id = Column('id', Integer, primary_key=True)
    requested_by = Column('requested_by', String(50), nullable=False)
    requested_on = Column('requested_on', Integer, nullable=False)
    status = Column('status', String(20), nullable=False)
    urls = Column('urls', String(99999), nullable=False)
    completed_on = Column('completed_on', Integer, nullable=True)

    def __init__(self, requested_by: str, requested_on: int, status: str, urls: str):
        self.requested_by = requested_by
        self.requested_on = requested_on
        self.status = status
        self.urls = urls
