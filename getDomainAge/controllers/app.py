"""
Routes and views for the app controller
"""

import os
import re
from datetime import datetime
from functools import wraps

from flask import (redirect, render_template, request, send_from_directory,
                   session, url_for)
from flask.wrappers import Response
from getDomainAge import app
from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler
from getDomainAge.models.database.tables import Job
from getDomainAge.models.enums import (Endpoint, FormParam, GetParam,
                                       HttpHeader, HttpMethod, JobStatus,
                                       SessionParam, SiteLink, Template)
from getDomainAge.models.forms.add_job import AddJobForm
from getDomainAge.services.database import DatabaseService
from getDomainAge.services.job import JobService
from getDomainAge.services.notification import NotificationService
from getDomainAge.services.ui import UIService

env = Environment()
logger = LogHandler.get_logger(env.app_name, env.log_path)
job_service = JobService()
db_service = DatabaseService()
notification_service = NotificationService()


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
            notification_service.notify_error('You are not logged it, please login to continue.')
            return redirect(url_for(SiteLink.HOMEPAGE.value))

    return inner_funtion


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
    print(session)

    # redirecting to dashboard for GET call and if use have logged in
    if request.method == HttpMethod.GET.value and SessionParam.LOGGED_IN.value in session.keys():
        session[SessionParam.PAGE_INDEX.value] = 2
        return redirect(url_for(SiteLink.DASHBOARD.value))

    # redirecting to index.html page for GET call and if user have not logged in
    if request.method == HttpMethod.GET.value:
        return render_template(Template.INDEX.value)

    # performing login operation for POST call and redirecting to dashboard
    if request.method == HttpMethod.POST.value:
        user_email = request.form[FormParam.EMAIL.value].lower()

        if user_email and re.fullmatch(r'[^@]+@[^@]+\.[^@]+', user_email, re.I):
            session[SessionParam.LOGGED_IN.value] = True
            session[SessionParam.VIEW_ALL.value] = False
            session[SessionParam.EMAIL.value] = user_email
            print("after updatez")
            print(session)
            logger.info(f'User with email {user_email} has logged in')
            return redirect(url_for(SiteLink.DASHBOARD.value))
        else:
            logger.warn(f'User entered email {user_email} is invalid')
            return render_template(Template.INDEX.value, error='Invalid email. Please enter a valid email.')


@app.route(f'/{Endpoint.DASHBOARD.value}', methods=[HttpMethod.GET.value])
@has_logged_in
def dashboard():
    """
    endpoint: /getDomainAge/dashboard
    dashboard endpoint which displays the application dashboard
    """
    # check if all jobs are loaded into memory, if not calling endpoint to load all jobs into memory
    job_service.update_job_cache()

    if request.args.get(GetParam.VIEW_ALL.value):
        session[SessionParam.VIEW_ALL.value] = True if request.args.get(GetParam.VIEW_ALL.value) == 'true' else False

    session[SessionParam.PAGE_INDEX.value] = 2 if session[SessionParam.VIEW_ALL.value] else 1

    try:
        page_number = int(request.args.get(GetParam.PAGE.value)) if request.args.get(GetParam.PAGE.value) else 1
    except ValueError:
        page_number = 1

    list_of_jobs = env.cached_jobs if session[SessionParam.VIEW_ALL.value] else [job for job in env.cached_jobs if job.requested_by.lower() == session[SessionParam.EMAIL.value]]
    number_of_jobs = len(list_of_jobs)

    max_page = int(number_of_jobs / env.app_job_per_page) + (0 if number_of_jobs % env.app_job_per_page == 0 else 1)
    previous_page, next_page = UIService().get_prev_next_page_number(max_page, page_number)
    valid_jobs = list_of_jobs[::-1][env.app_job_per_page * (page_number - 1):env.app_job_per_page * page_number]

    return render_template(Template.DASHBOARD.value, all_jobs=valid_jobs, page=page_number, last=max_page, start=previous_page, end=next_page)


@app.route(f'/{Endpoint.DOWNLOAD.value}/<filename>', methods=[HttpMethod.GET.value])
@has_logged_in
def download(filename):
    """
    endpoint: /getDomainAge/download/<filename>
    download endpoint for directly downloading the result file
    """
    # if filename is empty of filename is not in the form filename.ext
    try:
        job_id = filename.strip().split('.')[0]
    except Exception:
        notification_service.notify_error('Invalid filename.')
        return redirect(url_for(SiteLink.HOMEPAGE.value))

    # if filename is not a digit and contains some other character
    if not job_id or not re.match(r'[\d]', job_id):
        notification_service.notify_error('You have made an invalid request.')
        return redirect(url_for(SiteLink.HOMEPAGE.value))

    # fetching job record by job_id
    job_record = db_service.get_job(job_id)

    # checking if job_record is found and if the job was requested by the logged-in user
    if job_record and job_record.requested_by == session[SessionParam.EMAIL.value]:

        # if file is missing, notifying user
        if not os.path.exists(f'{env.result_directory}/job_id_{job_id}.csv'):
            notification_service.notify_warning('The result {}.csv that you are looking for is missing.'.format(job_id))
            return redirect(url_for(SiteLink.HOMEPAGE.value))

        # if file is present, starting the download
        return send_from_directory(directory=env.result_directory, filename=f'job_id_{job_id}.csv')
    else:
        # if job id was not created by this same email, showing warning message
        notification_service.notify_error('You do not have permission to download this file as you did not place the job.')
        return redirect(url_for(SiteLink.HOMEPAGE.value))


@app.route(f'/{Endpoint.JOB.value}', methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@has_logged_in
def job():
    """
    endpoing: /getDomainAge/job
    job endpoint for placing new job request
    """
    session[SessionParam.PAGE_INDEX.value] = 0
    add_job_form = AddJobForm(request.form)

    if request.method == HttpMethod.POST.value and add_job_form.validate():
        updated_urls = []

        # splitting URLs if user has used new lines
        parsed_urls = [id.replace('\n', '').strip() for id in add_job_form.urls.data.strip().split('\n')]

        # splitting URLs if user has used comma
        for url in parsed_urls:
            if ',' in url:
                updated_urls += [temp_id.strip() for temp_id in url.split(',')]
            else:
                updated_urls.append(url)

        # adding the new job in the database and notifying user
        new_job = Job(
            requested_by=session[SessionParam.EMAIL.value],
            requested_on=datetime.now(),
            status=JobStatus.PENDING.value,
            urls=','.join(updated_urls))
        db_service.add_job(new_job)
        notification_service.notify_success('Your job has been added, please wait for it to be processed.')

        logger.info(f'User {session[SessionParam.EMAIL.value]} has added a new job')

        # updating job cache
        job_service.update_job_cache()

        return redirect(url_for(SiteLink.DASHBOARD.value))

    return render_template(Template.JOB.value, form=add_job_form)


@app.route(f'/{Endpoint.LOGOUT.value}')
@has_logged_in
def logout():
    """
    endpoint: /getDomainAge/logout
    logout endpoint for user to logout
    """
    temp_email = session[SessionParam.EMAIL.value]
    session.clear()
    notification_service.notify_success('You have successfuly logged out')
    logger.info(f'User {temp_email} has logged out')
    return redirect(url_for(SiteLink.HOMEPAGE.value))


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


@app.errorhandler(404)
def error_404(e):
    """
    Handling 404 error
    """
    session[SessionParam.APP_VERSION.value] = env.app_version
    return render_template(Template.ERROR.value, code=404, message='Congratulation! You have discovered this secret page.')
