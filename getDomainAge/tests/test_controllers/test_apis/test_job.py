from unittest.mock import patch

import wtforms
from getDomainAge.models.enums import Endpoint, SessionParam
from getDomainAge.tests.test_controllers import app, do_login, test_client


def test_if_job_api_shows_add_job_page(test_client):
    do_login(test_client)  # performing login

    response = test_client.get(Endpoint.API_JOB.value)
    assert response.status_code == 200
    assert 'Add a new job' in response.data.decode('utf-8')

    with test_client.session_transaction() as session:
        assert SessionParam.PAGE_INDEX.value in session
        assert session[SessionParam.PAGE_INDEX.value] == 0


def test_if_job_api_adds_new_job(test_client):
    do_login(test_client)  # performing login

    # validating redirection code
    response = test_client.post(Endpoint.API_JOB.value, follow_redirects=False)
    assert response.status_code == 307

    # validating is redirected to correct endpoint
    response = test_client.post(Endpoint.API_JOB.value, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == Endpoint.API_JOB_ADD.value


def test_job_view_api_for_requestor_jobs(test_client):
    do_login(test_client)  # performing login

    response = test_client.get(Endpoint.API_JOB_VIEW.value, follow_redirects=False)
    assert response.status_code == 200
    print(response.data.decode('utf-8'))
    assert 'List of jobs submitted by you' in response.data.decode('utf-8')

    with test_client.session_transaction() as session:
        assert SessionParam.PAGE_INDEX.value in session
        assert SessionParam.VIEW_ALL.value in session

        assert not session[SessionParam.VIEW_ALL.value]
        assert session[SessionParam.PAGE_INDEX.value] == 1


def test_job_view_api_for_all_jobs(test_client):
    do_login(test_client)  # performing login

    response = test_client.get(f'{Endpoint.API_JOB_VIEW.value}?all', follow_redirects=False)
    assert response.status_code == 200
    assert 'List of jobs submitted by all user' in response.data.decode('utf-8')

    with test_client.session_transaction() as session:
        assert SessionParam.PAGE_INDEX.value in session
        assert SessionParam.VIEW_ALL.value in session

        assert session[SessionParam.VIEW_ALL.value]
        assert session[SessionParam.PAGE_INDEX.value] == 2


def test_if_job_add_api_redirects_to_add_job_page_with_missing_data(test_client):
    do_login(test_client)  # performing login

    response = test_client.post(Endpoint.API_JOB_ADD.value, follow_redirects=True)
    assert response.status_code == 200
    assert 'Add a new job' in response.data.decode('utf-8')


def test_job_addition_via_job_add_endpoint(test_client):
    do_login(test_client)  # performing login

    with patch.object(wtforms.Form, 'validate', return_value=True) as _:
        response = test_client.post(Endpoint.API_JOB_ADD.value, follow_redirects=False)
        assert response.status_code == 302
        # assert 'Failed to added new job, please try aftersome.' in response.data.decode('utf-8')

        # TODO: Test for redirected page with when flask>2.0.1 is released


def test_job_result_download_with_invalid_id(test_client):
    do_login(test_client)  # performing login

    response = test_client.get(f'{Endpoint.API_JOB_DOWNLOAD.value}/ABC', follow_redirects=False)
    assert response.status_code == 302

    # TODO: Test for redirected page with when flask>2.0.1 is released
    # response = test_client.get(f'{Endpoint.API_JOB_DOWNLOAD.value}/ABC', follow_redirects=True)
    # assert response.status_code == 200
    # assert response.request.path == Endpoint.APP_NAME.value
    # assert 'You have made an invalid request.' in response.data.decode('utf-8')
