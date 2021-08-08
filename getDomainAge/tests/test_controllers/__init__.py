import pytest
from getDomainAge.handlers.environment import Environment
from getDomainAge.models.enums import Endpoint
from getDomainAge.tests.mocked_util import MockedUtil


@pytest.fixture
def app():
    # creating and initializing the environment
    # from getDomainAge.handlers.environment import Environment
    # from getDomainAge.tests.mocked_util import MockedUtil
    env = Environment()
    env.initialize(MockedUtil().get_valid_configs())

    # import the flask app
    # import all the app endpoints
    import getDomainAge.controllers.app
    from getDomainAge import app as flask_app
    # importing database service class and initializing the database
    from getDomainAge.services.database import DatabaseService
    DatabaseService().initialize(recreate=True)

    flask_app.testing = True
    flask_app.secret_key = env.api_secrect_key

    yield flask_app


@pytest.fixture
def test_client(app):
    # creating and returning a test client
    return app.test_client()


def do_login(test_client, email='test@test.com'):
    test_client.post(Endpoint.API_LOGIN.value, data={'email': email}, follow_redirects=False)
