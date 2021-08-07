from getDomainAge.models.enums import (Endpoint, FormParam, HttpHeader,
                                       HttpMethod, JobStatus,
                                       NotificationCategory, RequestParam,
                                       SessionParam, SiteLink, Template)


def test_endpoint():
    expected_endpoints = {'ROOT': '/',
                          'APP_NAME': '/getDomainAge',
                          'DASHBOARD': '/getDomainAge/dashboard',
                          'API': '/getDomainAge/api',
                          'API_LOGIN': '/getDomainAge/api/login',
                          'API_LOGOUT': '/getDomainAge/api/logout',
                          'API_JOB': '/getDomainAge/api/job',
                          'API_JOB_ADD': '/getDomainAge/api/job/add',
                          'API_JOB_VIEW': '/getDomainAge/api/job/view',
                          'API_JOB_DOWNLOAD': '/getDomainAge/api/job/download'
                          }

    for _item in Endpoint:
        assert _item.name in expected_endpoints.keys()
        assert _item.value == expected_endpoints[_item.name]


def test_form_param():
    expected_form_params = {'EMAIL': 'email'}

    for _item in FormParam:
        assert _item.name in expected_form_params.keys()
        assert _item.value == expected_form_params[_item.name]


def test_http_header():
    expected_http_header = 'API_KEY'

    for _item in HttpHeader:
        assert _item.name is expected_http_header
        assert _item.value is expected_http_header


def test_http_method():
    expected_http_methods = ['GET', 'POST']

    for _item in HttpMethod:
        assert _item.name in expected_http_methods
        assert _item.value in expected_http_methods


def test_job_status():
    expected_job_status = {'RUNNING': 'RUNNING',
                           'PENDING': 'PENDING',
                           'COMPLETED': 'COMPLETED',
                           'FAILED_EMAIL': 'MAIL FAILED'
                           }

    for _item in JobStatus:
        assert _item.name in expected_job_status.keys()
        assert _item.value == expected_job_status[_item.name]


def test_notification_category():
    expected_job_status = ['SUCCESS', 'WARNING', 'DANGER']

    for _item in NotificationCategory:
        assert _item.name in expected_job_status
        assert _item.value.upper() in expected_job_status


def test_request_params():
    expected_request_params = {'VIEW_ALL': 'viewall',
                               'PAGE': 'page',
                               'EMAIL': 'email',
                               'API_KEY': 'api_key',
                               'ALL': 'all'
                               }

    for _item in RequestParam:
        assert _item.name in expected_request_params.keys()
        assert _item.value == expected_request_params[_item.name]


def test_session_params():
    expected_session_params = {'APP_VERSION': 'app_version',
                               'EMAIL': 'email',
                               'LOGGED_IN': 'logged_in',
                               'PAGE_INDEX': 'page_index',
                               'VIEW_ALL': 'viewall'
                               }

    for _item in SessionParam:
        assert _item.name in expected_session_params.keys()
        assert _item.value == expected_session_params[_item.name]


def test_sitelink():
    expected_site_links = ['HOMEPAGE', 'DASHBOARD', 'LOGIN']

    for _item in SiteLink:
        assert _item.name in expected_site_links
        assert _item.value.upper() in expected_site_links


def test_templates():
    expected_site_links = {'INDEX': 'index.html',
                           'VIEW_JOBS': 'view_jobs.html',
                           'ADD_JOB': 'add_job.html',
                           'ERROR': 'error.html'
                           }

    for _item in Template:
        assert _item.name in expected_site_links.keys()
        assert _item.value == expected_site_links[_item.name]
