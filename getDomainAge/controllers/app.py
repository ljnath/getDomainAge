"""
Routes and views for the app controller
"""

import getDomainAge.controllers.apis.job
import getDomainAge.controllers.apis.login
import getDomainAge.controllers.error
from flask import redirect, render_template, request, session, url_for
from flask.wrappers import Response
from getDomainAge import app
from getDomainAge.controllers import has_logged_in
from getDomainAge.handlers.environment import Environment
from getDomainAge.models.enums import (Endpoint, HttpHeader, HttpMethod,
                                       SessionParam, SiteLink, Template)
from getDomainAge.models.forms.add_job import AddJobForm
from getDomainAge.services.database import DatabaseService
from getDomainAge.services.job import JobService
from getDomainAge.services.login import LoginService
from getDomainAge.services.notification import NotificationService

env = Environment()
job_service = JobService()
db_service = DatabaseService()
notification_service = NotificationService()
login_service = LoginService()


@app.route(Endpoint.ROOT.value, methods=[HttpMethod.GET.value])
def root():
    """
    endpoint: /
    """
    return redirect(url_for(SiteLink.HOMEPAGE.value), code=301)


@app.route(f'/{Endpoint.APP_NAME.value}', methods=[HttpMethod.GET.value, HttpMethod.POST.value])
def homepage():
    """
    endpoint: /getDomainAge ; accepts both POST and GET
    """
    # storing app version in session variable for UI
    session[SessionParam.APP_VERSION.value] = env.app_version

    # redirecting to dashboard for GET call and if use have logged in
    if request.method == HttpMethod.GET.value and SessionParam.LOGGED_IN.value in session.keys():
        session[SessionParam.PAGE_INDEX.value] = 2
        return redirect(url_for(SiteLink.DASHBOARD.value))

    # redirecting to index.html page for GET call and if user have not logged in
    if request.method == HttpMethod.GET.value:
        return render_template(Template.INDEX.value)

    # performing login operation for POST call and redirecting to dashboard
    if request.method == HttpMethod.POST.value:
        return redirect(Endpoint.API_LOGIN.value, code=307)


@app.route(f'/{Endpoint.DASHBOARD.value}', methods=[HttpMethod.GET.value])
@has_logged_in
def dashboard():
    """
    endpoint: /getDomainAge/dashboard
    dashboard endpoint which displays the application dashboard
    """
    return redirect(Endpoint.API_JOB_VIEW.value, code=307)


@app.route(f'/{Endpoint.API_JOB.value}', methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@has_logged_in
def job():
    """
    endpoing: /getDomainAge/job
    job endpoint for placing new job request
    """
    session[SessionParam.PAGE_INDEX.value] = 0
    add_job_form = AddJobForm(request.form)

    if request.method == HttpMethod.POST.value:
        return redirect(Endpoint.API_JOB_ADD.value, code=307)

    return render_template(Template.JOB.value, form=add_job_form)


@app.route(f'/{Endpoint.RELOAD_CACHE.value}', methods=[HttpMethod.POST.value])
def update_cache():
    """
    endpoint: /getDomainAge/job/update
    Method to update the local job cache
    :param : force as boolean if the cache update needs to be forcefully done
    """
    if request.headers[HttpHeader.API_KEY.value] == env.api_secrect_key:
        env.cached_jobs = db_service.get_all_jobs()

    # TODO: try to return valid HTTP code 204
    return Response("{'status':'cache refeshed'}", status=204, mimetype='application/json')
