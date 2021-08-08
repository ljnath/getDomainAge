from getDomainAge.models.enums import Endpoint, SessionParam
from getDomainAge.tests.test_controllers import app, do_login, test_client


def test_login_endpoint_with_invalid_method(test_client):
    with test_client:
        response = test_client.get(Endpoint.API_LOGIN.value)
        assert response.status_code == 405


def test_login_endpoint_with_invalid_form_data(test_client):
    invalid_emails = ['abc', 'abc@abc', 'abc@abc.']
    with test_client:
        for _email in invalid_emails:
            response = test_client.post(Endpoint.API_LOGIN.value, data={'email': _email}, follow_redirects=True)
            assert response.status_code == 200
            assert 'Login failed, Invalid email ID.' in response.data.decode('utf-8')


def test_login_endpoint_with_valid_form_data(app, test_client):
    # testing login api with valid data
    response = test_client.post(Endpoint.API_LOGIN.value, data={'email': 'test@test.com'})
    assert response.status_code == 302

    # validating session parameters
    with test_client.session_transaction() as session:
        assert SessionParam.LOGGED_IN.value in session
        assert SessionParam.VIEW_ALL.value in session
        assert SessionParam.EMAIL.value in session

        assert session[SessionParam.LOGGED_IN.value]
        assert not session[SessionParam.VIEW_ALL.value]
        assert session[SessionParam.EMAIL.value] == 'test@test.com'

    # testing /getDomainAge enpoint after login
    response = test_client.get(Endpoint.APP_NAME.value, follow_redirects=False)
    assert response.status_code == 302

    # validating session parameters
    with test_client.session_transaction() as session:
        assert SessionParam.PAGE_INDEX.value in session
        assert session[SessionParam.PAGE_INDEX.value] == 2


def test_logout(test_client):
    do_login(test_client)  # performing login

    # calling logout
    response = test_client.get(Endpoint.API_LOGOUT.value, follow_redirects=True)
    assert response.status_code == 200
    assert 'You have successfuly logged out' in response.data.decode('utf-8')
