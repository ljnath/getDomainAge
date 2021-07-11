from functools import wraps

from flask import redirect, session, url_for
from getDomainAge.models.enums import SessionParam, SiteLink
from getDomainAge.services.notification import NotificationService


def has_logged_in(calling_function):
    """
    decorator to check if user has logged in
    """
    @wraps(calling_function)
    def inner_funtion(*args, **kwargs):
        if SessionParam.LOGGED_IN.value in session:
            # is user has logged in, then invoking the calling function
            return calling_function(*args, **kwargs)
        else:
            # if not showing message on UI and redirecting to landing page
            NotificationService().notify_error('You are not logged it, please login to continue.')
            return redirect(url_for(SiteLink.HOMEPAGE.value))

    return inner_funtion
