import sqlalchemy
from getDomainAge.handlers.environment import Environment
from getDomainAge.tests.mocked_util import MockedUtil


def test_jobs_table_schema():
    env = Environment()
    env.initialize(MockedUtil().get_valid_configs())

    from getDomainAge.models.database.tables import Jobs

    assert Jobs.__tablename__ == 'Jobs'

    # testing ID column
    assert Jobs.id.name == 'id'
    assert isinstance(Jobs.id.type, sqlalchemy.Integer)
    assert Jobs.id.primary_key

    # testing requested_by column
    assert Jobs.requested_by.name == 'requested_by'
    assert isinstance(Jobs.requested_by.type, sqlalchemy.String)
    assert Jobs.requested_by.type.length == 50
    assert not Jobs.requested_by.primary_key
    assert not Jobs.requested_by.nullable

    # testing requested_on column
    assert Jobs.requested_on.name == 'requested_on'
    assert isinstance(Jobs.requested_on.type, sqlalchemy.Integer)
    assert not Jobs.requested_on.primary_key
    assert not Jobs.requested_on.nullable

    # testing status column
    assert Jobs.status.name == 'status'
    assert isinstance(Jobs.status.type, sqlalchemy.String)
    assert Jobs.status.type.length == 20
    assert not Jobs.status.primary_key
    assert not Jobs.status.nullable

    # testing urls column
    assert Jobs.urls.name == 'urls'
    assert isinstance(Jobs.urls.type, sqlalchemy.String)
    assert Jobs.urls.type.length == 99999
    assert not Jobs.urls.primary_key
    assert not Jobs.urls.nullable

    # testing completed_on column
    assert Jobs.completed_on.name == 'completed_on'
    assert isinstance(Jobs.completed_on.type, sqlalchemy.Integer)
    assert not Jobs.completed_on.primary_key
    assert Jobs.completed_on.nullable

    Environment.clear()
