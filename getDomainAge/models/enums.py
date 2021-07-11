from enum import Enum


class Endpoint(Enum):
    """
    Endpoint enum stores all the supported enfpoints in this application
    Storing all these as enums prevents typos in code and improves future maintainability

    Nested endpoints are created using the enum members
    """
    ROOT = '/'
    APP_NAME = f'{ROOT}getDomainAge'
    DASHBOARD = f'{APP_NAME}/dashboard'

    API = f'{APP_NAME}/api'

    API_LOGIN = f'{API}/login'
    API_LOGOUT = f'{API}/logout'

    API_JOB = f'{API}/job'
    API_JOB_ADD = f'{API_JOB}/add'
    API_JOB_VIEW = f'{API_JOB}/view'
    API_JOB_DOWNLOAD = f'{API_JOB}/download'


class FormParam(Enum):
    """
    FormParam enum stores all the supported FORM parameters used in this application.
    These parameters are passed while submitting FORMs
    Storing all these as enums prevents typos in code and improves future maintainability
    """
    EMAIL = 'email'


class HttpHeader(Enum):
    """"
    HttpHeader enum stores all the header parameters that are used in this application
    Storing all these as enums prevents typos in code and improves future maintainability
    """
    API_KEY = 'API_KEY'


class HttpMethod(Enum):
    """
    HttpMethod enum stores the HTTP verbs ot methods and the corresponding string text as value
    Storing all these as enums prevents typos in code and improves future maintainability
    """
    GET = 'GET'
    POST = 'POST'


class JobStatus(Enum):
    """
    JobStatus enum stores all possible state of a job
    """
    RUNNING = 'RUNNING'
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'


class NotificationCategory(Enum):
    """
    NotificationCategory enum stores various categories used while flashing message in the UI
    """
    SUCCESS = 'success'
    WARNING = 'warning'
    FAILURE = 'failure'
    DANGER = 'danger'


class RequestParam(Enum):
    """
    RequestParam enum stores all the supported GET and POST parameters used in this application
    These parameters are passed while making a GET/POST call
    Storing all these as enums prevents typos in code and improves future maintainability
    """
    VIEW_ALL = 'viewall'
    PAGE = 'page'
    EMAIL = 'email'
    API_KEY = 'api_key'
    ALL = 'all'


class SessionParam(Enum):
    """
    SessionParam enum stores all the session parameter that are used throughout this application.
    Storing all these as enums prevents typos in code and improves future maintainability
    """
    APP_VERSION = 'app_version'
    EMAIL = 'email'
    LOGGED_IN = 'logged_in'
    PAGE_INDEX = 'page_index'
    VIEW_ALL = 'viewall'


class SiteLink(Enum):
    """
    SiteLink enum stores all the links in the website with the name of the links as value.
    This is used to auto-construct the URL redirecting based on method names
    """
    HOMEPAGE = 'homepage'
    DASHBOARD = 'dashboard'
    LOGIN = 'login'


class Template(Enum):
    """
    Template enum stores all the HTML templates with repective filename as value
    This is used while rendering
    """
    INDEX = 'index.html'
    VIEW_JOBS = 'view_jobs.html'
    ADD_JOB = 'add_job.html'
    ERROR = 'error.html'
