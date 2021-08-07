import pytest
from getDomainAge.handlers.environment import Environment
from getDomainAge.models.enums import SessionParam
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
    DatabaseService().initialize()

    flask_app.testing = True
    flask_app.secret_key = env.api_secrect_key

    yield flask_app


@pytest.fixture
def client(app):
    # creating and returning a test client
    return app.test_client()


def test_root_endpoint(client):
    with client:
        response = client.get('/')
        assert response.status_code == 301


def test_root_endpoint_redirect(client):
    with client:
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/getDomainAge'


def test_root_endpoint_with_invalid_method(client):
    with client:
        response = client.post('/', follow_redirects=True)
        assert response.status_code == 405


def test_homepage(client):
    with client:
        response = client.get('/getDomainAge')
        assert response.status_code == 200
        assert 'Welcome To getDomainAge !' in response.data.decode('utf-8')

        with client.session_transaction() as session:
            assert SessionParam.APP_VERSION.value in session
            assert session[SessionParam.APP_VERSION.value] == Environment().app_version


def test_login_endpoint_with_invalid_method(client):
    with client:
        response = client.get('/getDomainAge/api/login')
        assert response.status_code == 405


def test_login_endpoint_with_invalid_form_data(client):
    invalid_emails = ['abc', 'abc@abc', 'abc@abc.']
    with client:
        for _email in invalid_emails:
            response = client.post('/getDomainAge/api/login', data={'email': _email}, follow_redirects=True)
            assert response.status_code == 200
            assert 'Login failed, Invalid email ID.' in response.data.decode('utf-8')


def test_login_endpoint_with_valid_form_data(client):
    with client:
        response = client.post('/getDomainAge/api/login', data={'email': 'test@test.com'})
        assert response.status_code == 302

        with client.session_transaction() as session:
            assert SessionParam.LOGGED_IN.value in session
            assert SessionParam.VIEW_ALL.value in session
            assert SessionParam.EMAIL.value in session

            assert session[SessionParam.LOGGED_IN.value]
            assert not session[SessionParam.VIEW_ALL.value]
            assert session[SessionParam.EMAIL.value] == 'test@test.com'
