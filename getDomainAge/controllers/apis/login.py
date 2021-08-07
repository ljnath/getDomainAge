from flask import redirect, render_template, request, url_for
from getDomainAge import app
from getDomainAge.controllers import has_logged_in
from getDomainAge.models.enums import (Endpoint, FormParam, HttpMethod,
                                       SiteLink, Template)
from getDomainAge.services.login import LoginService
from getDomainAge.services.notification import NotificationService

notification_service = NotificationService()
login_service = LoginService()


@app.route(f'/{Endpoint.API_LOGIN.value}', methods=[HttpMethod.POST.value])
def api_login():
    """
    endpoint: /getDomainAge/api/login
    login endpoint for user to login into the app
    """
    user_email = request.form[FormParam.EMAIL.value].lower()

    if login_service.login(user_email):
        return redirect(url_for(SiteLink.DASHBOARD.value))
    else:
        return render_template(Template.INDEX.value, error='Login failed, Invalid email ID.')


@app.route(f'/{Endpoint.API_LOGOUT.value}')
@has_logged_in
def api_logout():
    """
    endpoint: /getDomainAge/api/logout
    logout endpoint for user to logout
    """
    login_service.logout()
    notification_service.notify_success('You have successfuly logged out')
    return redirect(url_for(SiteLink.HOMEPAGE.value))
