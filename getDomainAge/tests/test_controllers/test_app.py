from getDomainAge.handlers.environment import Environment
from getDomainAge.models.enums import Endpoint, SessionParam
from getDomainAge.tests.test_controllers import app, do_login, test_client


def test_root_endpoint(test_client):
    with test_client:
        response = test_client.get(Endpoint.ROOT.value)
        assert response.status_code == 301


def test_root_endpoint_redirect(test_client):
    with test_client:
        response = test_client.get(Endpoint.ROOT.value, follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == Endpoint.APP_NAME.value


def test_root_endpoint_with_invalid_method(test_client):
    with test_client:
        response = test_client.post(Endpoint.ROOT.value, follow_redirects=True)
        assert response.status_code == 405


def test_homepage(test_client):
    with test_client:
        response = test_client.get(Endpoint.APP_NAME.value)
        assert response.status_code == 200
        assert 'Welcome To getDomainAge !' in response.data.decode('utf-8')

        with test_client.session_transaction() as session:
            assert SessionParam.APP_VERSION.value in session
            assert session[SessionParam.APP_VERSION.value] == Environment().app_version


def test_homepage_login_redirection(test_client):
    with test_client:
        response = test_client.post(Endpoint.APP_NAME.value, follow_redirects=False)
        assert response.status_code == 307

        # cannot test the final URL becuase flask fails when follow_redirects is set to True
        # issue - https://github.com/pallets/werkzeug/issues/2148
        # issue is merged
        # TODO: Test when flask>2.0.1 is released
        # # assert response.request.path == '/getDomainAge/api/login'


def test_dashboard_endpoint(test_client):
    do_login(test_client)   # performing login
    response = test_client.get(Endpoint.DASHBOARD.value, follow_redirects=False)
    assert response.status_code == 307

    response = test_client.get(Endpoint.DASHBOARD.value, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == Endpoint.API_JOB_VIEW.value
